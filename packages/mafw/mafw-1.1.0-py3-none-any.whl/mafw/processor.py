"""
Module implements the basic Processor class, the ProcessorList and all helper classes to achieve the core
functionality of the MAFw.
"""

from __future__ import annotations

import contextlib
import inspect
import logging
import warnings
from collections.abc import Callable, Iterator
from copy import copy
from functools import wraps
from itertools import count
from typing import Any, Collection, Generic, Iterable, Self, SupportsIndex, TypeVar, Union, cast

import peewee
from peewee import Database

# noinspection PyUnresolvedReferences
from playhouse.db_url import connect

import mafw.db.db_filter
from mafw.active import Active
from mafw.db.db_model import database_proxy
from mafw.db.db_types import PeeweeModelWithMeta
from mafw.db.std_tables import standard_tables
from mafw.enumerators import LoopingStatus, LoopType, ProcessorExitStatus, ProcessorStatus
from mafw.mafw_errors import (
    AbortProcessorException,
    MissingDatabase,
    MissingOverloadedMethod,
    MissingSuperCall,
    ProcessorParameterError,
)
from mafw.timer import Timer, pretty_format_duration
from mafw.tools.regexp import extract_protocol
from mafw.ui.abstract_user_interface import UserInterfaceBase
from mafw.ui.console_user_interface import ConsoleInterface

log = logging.getLogger(__name__)

ParameterType = TypeVar('ParameterType')
"""Generic variable type for the :class:`ActiveParameter` and :class:`PassiveParameter`."""


def validate_database_conf(database_conf: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """
    Validates the database configuration.

    :param database_conf: The input database configuration. Defaults to None.
    :type database_conf: dict, Optional
    :return: Either the validated database configuration or None if it is invalid.
    :rtype: dict, None
    """
    if database_conf is None:
        return None

    # dict is mutable, if I change it inside the function, I change it also outside.
    conf = database_conf.copy()

    if 'DBConfiguration' in conf:
        # the database_conf is the steering file. Extract the DBConfiguration table
        conf = conf['DBConfiguration']
    required_fields = ['URL']
    if all([field in conf for field in required_fields]):
        return database_conf
    else:
        return None


class PassiveParameter(Generic[ParameterType]):
    """
    A processor parameter that can be registered and configured.

    For Processors to perform their analytical task, it may be necessary to have some configurable parameters,
    like a DB input table or the output folder or a numeric parameter.

    The name of the parameter must be unique within the Processor scope and a valid python identifier.

    When defined as a PassiveParameter, an instance variable can have a default value if the user did not provide
    one, and it is much easier to configure via a configuration file.

    A parameter for which only a default value is provided is automatically considered *optional*.

    If both the value and the default value are not provided, an exception is raised.

    This class is working behind the scene, that is why it is named **passive**. The user will very likely add class
    instances of :class:`ActiveParameter`, that are publicly exposed in the processor class namespace,
    and an PassiveParameter will automatically added to the class. To access this passive parameter the user
    can use the :meth:`Processor.get_parameter` using the name as key. The :attr:`value` of the passive parameter is
    always accessible using calling the corresponding ActiveParameter.

    .. seealso::

        An explanation on how processor parameters work and should be used is given in :ref:`Understanding processor
        parameters <parameters>`
    """

    def __init__(
        self, name: str, value: ParameterType | None = None, default: ParameterType | None = None, help_doc: str = ''
    ):
        """
        Constructor parameters:

        :param name: The name of the parameter. It must be a valid python identifier.
        :type name: str
        :param value: The set value of the parameter. If None, then the default value will be used. Defaults to None.
        :type value: ParameterType, Optional
        :param default: The default value for the parameter. It is used if the :attr:`value` is not provided. Defaults to None.
        :type default: ParameterType, Optional
        :param help_doc: A brief explanation of the parameter.
        :type help_doc: str, Optional
        :raises ProcessorParameterError: if both `value` and `default` are not provided or if `name` is not a valid identifier.
        """
        if not name.isidentifier():
            raise ProcessorParameterError(f'{name} is not a valid python identifier.')

        self.name = name

        if value is not None:
            self._value: ParameterType = value
            self._is_set = True
            self._is_optional = False
        elif default is not None:
            self._value = default
            self._is_set = False
            self._is_optional = True
        else:
            raise ProcessorParameterError('Processor parameter cannot have both value and default value set to None')

        self.doc = help_doc

    def __rich_repr__(self) -> Iterator[Any]:
        yield 'name', self.name
        yield 'value', self.value, None
        yield 'help_doc', self.doc, ''

    @property
    def is_set(self) -> bool:
        """
        Property to check if the value has been set.

        It is useful for optional parameter to see if the current value is the default one, or if the user set it.
        """
        return self._is_set

    @property
    def value(self) -> ParameterType:
        """
        Gets the parameter value.

        :return: The parameter value.
        :rtype: ParameterType
        :raises ProcessorParameterError: if both value and default were not defined.
        """
        return self._value

    @value.setter
    def value(self, value: ParameterType) -> None:
        """
        Sets the parameter value.

        :param value: The value to be set.
        :type value: ParameterType
        """
        self._value = value
        self._is_set = True

    @property
    def is_optional(self) -> bool:
        """
        Property to check if the parameter is optional.

        :return: True if the parameter is optional
        :rtype: bool
        """
        return self._is_optional

    def __repr__(self) -> str:
        args = ['name', 'value', 'doc']
        return '{klass}({attrs})'.format(
            klass=self.__class__.__name__,
            attrs=', '.join('{}={!r}'.format(k, v) for k, v in self.__dict__.items() if k in args),
        )


F = TypeVar('F', bound=Callable[..., Any])
"""Type variable for generic callable with any return value."""


def ensure_parameter_registration(func: F) -> F:
    """Decorator to ensure that before calling `func` the processor parameters have been registered."""

    @wraps(func)
    def wrapper(*args: Processor, **kwargs: Any) -> F:
        # the first positional arguments must be self
        if len(args) == 0:
            raise ProcessorParameterError(
                'Attempt to apply the ensure_parameter_registration to something different to a Processor subclass.'
            )
        self = args[0]
        if not isinstance(self, Processor):
            raise ProcessorParameterError(
                'Attempt to apply the ensure_parameter_registration to something different to a Processor subclass.'
            )
        if self._parameter_registered is False:
            self._register_parameters()
        return cast(F, func(*args, **kwargs))

    return cast(F, wrapper)


class ActiveParameter(Generic[ParameterType]):
    r"""
    The public interface to the processor parameter.

    The behaviour of a :class:`Processor` can be customized by using processor parameters. The value of these
    parameters can be either set via a configuration file or directly when creating the class.

    If the user wants to benefit from this facility, they have to add in the instance of the Processor subclass an
    ActiveParameter instance in this way:

    .. code-block::

        class MyProcessor(Processor):

            # this is the input folder
            input_folder = ActiveParameter('input_folder', Path(r'C:\'), help_doc='This is where to look for input files')

            def __init__(self, *args, **kwargs):
                super().__init(*args, **kwargs)

                # change the input folder to something else
                self.input_folder = Path(r'D:\data')

                # get the value of the parameter
                print(self.input_folder)

    The ActiveParameter is a `descriptor <https://docs.python.org/3/glossary.html#term-descriptor>`_, it means that
    when you create one of them, a lot of work is done behind the scene.

    In simple words, a processor parameter is made by two objects: a public interface where the user can easily
    access the value of the parameter and a private interface where all other information (default, documentation...)
    is also stored.

    The user does not have to take care of all of this. When a new ActiveParameter instance is added to the class as
    in the code snipped above, the private interface is automatically created and will stay in the class instance
    until the end of the class lifetime.

    To access the private interface, the user can use the :meth:`Processor.get_parameter` method using the parameter
    name as a key.

    .. seealso::

        The private counter part in the :class:`PassiveParameter`.

    """

    def __init__(
        self, name: str, value: ParameterType | None = None, default: ParameterType | None = None, help_doc: str = ''
    ):
        """
        Constructor parameters:

        :param name: The name of the parameter.
        :type name: str
        :param value: The initial value of the parameter. Defaults to None.
        :type value: ParameterType, Optional
        :param default: The default value of the parameter, to be used when ``value`` is not set., Defaults to None.
        :type default: ParameterType, Optional
        :param help_doc: An explanatory text describing the parameter.
        :type help_doc: str, Optional
        """

        self._value = value
        self._default = default
        self._help_doc = help_doc
        self._external_name = name

    def __set_name__(self, owner: type[Processor], name: str) -> None:
        self.public_name = name
        self.private_name = f'param_{name}'
        self._owner = owner

        if not hasattr(owner, self.private_name):
            setattr(
                owner,
                self.private_name,
                PassiveParameter(self._external_name, self._value, self._default, self._help_doc),
            )

    def __get__(self, obj: Processor, obj_type: type[Processor]) -> ActiveParameter[ParameterType] | ParameterType:
        if obj is None:
            return self

        param: PassiveParameter[ParameterType] = getattr(obj, self.private_name)
        return param.value

    def __set__(self, obj: Processor, value: ParameterType) -> None:
        param: PassiveParameter[ParameterType] = getattr(obj, self.private_name)
        param.value = value


class ProcessorMeta(type):
    """A metaclass to implement the post-init method."""

    def __call__(cls, *args: Any, **kwargs: Any) -> 'ProcessorMeta':
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__()
        return cast(ProcessorMeta, obj)


# noinspection PyProtectedMember
class Processor(metaclass=ProcessorMeta):
    """
    The basic processor.

    A very comprehensive description of what a Processor does and how it works is available at :ref:`doc_processor`.
    """

    processor_status = Active(ProcessorStatus.Unknown)
    """Processor execution status"""

    looping_status = Active(LoopingStatus.Continue)
    """Looping modifier"""

    progress_message: str = f'{__qualname__} is working'
    """Message displayed to show the progress. 
    
    It can be customized with information about the current item in the loop by overloading the 
    :meth:`format_progress_message`."""

    _ids = count(0)
    """A counter for all processor instances"""

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        config: dict[str, Any] | None = None,
        looper: LoopType | str = LoopType.ForLoop,
        user_interface: UserInterfaceBase | None = None,
        timer: Timer | None = None,
        timer_params: dict[str, Any] | None = None,
        database: Database | None = None,
        database_conf: dict[str, Any] | None = None,
        remove_orphan_files: bool = True,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Constructor parameters

        :param name: The name of the processor. If None is provided, the class name is used instead. Defaults to None.
        :type name: str, Optional
        :param description: A short description of the processor task. Defaults to the processor name.
        :type description: str, Optional
        :param config: A configuration dictionary for this processor. Defaults to None.
        :type config: dict, Optional
        :param looper: Enumerator to define the looping type. Defaults to LoopType.ForLoop
        :type looper: LoopType, Optional
        :param user_interface: A user interface instance to be used by the processor to interact with the user.
        :type user_interface: UserInterfaceBase, Optional
        :param timer: A timer object to measure process duration.
        :type timer: Timer, Optional
        :param timer_params: Parameters for the timer object.
        :type timer_params: dict, Optional
        :param database: A database instance. Defaults to None.
        :type database: Database, Optional
        :param database_conf: Configuration for the database. Default to None.
        :type database_conf: dict, Optional
        :param remove_orphan_files: Boolean flag to remove files on disc without a reference to the database.
            See :ref:`std_tables` and :meth:`~mafw.processor.Processor._remove_orphan_files`. Defaults to True
        :type remove_orphan_files: bool, Optional
        :param kwargs: Keyword arguments that can be used to set processor parameters.
        """

        self.name = name or self.__class__.__name__
        """The name of the processor."""

        self.unique_id = next(self._ids)
        """A unique identifier representing how many instances of Processor has been created."""

        self.description = description or self.name
        """A short description of the processor task."""

        self.item: Any = None
        """The current item of the loop."""

        self.processor_exit_status = ProcessorExitStatus.Successful
        """Processor exit status"""

        self.loop_type: LoopType = LoopType(looper)
        """
        The loop type. 
        
        The value of this parameter can also be changed by the :func:`~mafw.decorators.execution_workflow` decorator 
        factory.  
        
        See :class:`~mafw.enumerators.LoopType` for more details.
        """

        # private attributes
        self._config = config or {}
        self._processor_parameters: dict[str, PassiveParameter[ParameterType]] = {}  # type: ignore
        # wait for answer from SO
        self._parameter_registered = False
        self._kwargs = kwargs

        # loops attributes
        self._i_item: int = -1
        self._n_item: int | None = -1
        self._process_durations: list[float] = []

        # resource stack
        self._resource_stack: contextlib.ExitStack
        self._resource_acquisition: bool = True

        # processor timer
        self.timer: Timer | None = timer
        self._timer_parameters: dict[str, Any] = timer_params or {}

        # user interface
        if user_interface is None:
            self._user_interface: UserInterfaceBase = ConsoleInterface()
        else:
            self._user_interface = user_interface

        # database stuff
        self._database: peewee.Database | None = database
        self._database_conf: dict[str, Any] | None = validate_database_conf(database_conf)
        self.filter_register: mafw.db.db_filter.FilterRegister = mafw.db.db_filter.FilterRegister()
        """The DB filter register of the Processor."""
        self.remove_orphan_files: bool = remove_orphan_files
        """The flag to remove or protect the orphan files. Defaults to True"""

        # sub-classing stuff
        # todo:
        #   should we make it a class attribute instead of an instance attribute?
        self._methods_to_be_checked_for_super = [('start', Processor), ('finish', Processor)]
        """
        List of methods to be checked for super inclusion.
        
        It is a list of tuple, with the first element the name of the method to be checked and the second the base 
        class to the be compared.
        """

    def __post_init__(self) -> None:
        self._register_parameters()
        self._load_parameter_configuration()
        self._overrule_kws_parameters()
        self._check_method_overload()
        self._check_method_super()
        self.processor_status = ProcessorStatus.Init

    def _register_parameters(self) -> None:
        for attr_name in dir(self):
            if attr_name in [
                'database'
            ]:  # database is a property that might be not yet initialised and will throw an exception
                continue
            attr = getattr(self, attr_name)
            if isinstance(attr, PassiveParameter):
                if attr.name in self._processor_parameters:
                    raise ProcessorParameterError(f'Duplicated parameter name ({attr_name}.')
                self._processor_parameters[attr.name] = attr
        self._parameter_registered = True

    @ensure_parameter_registration
    def _load_parameter_configuration(self) -> None:
        original_config = copy(self._config)
        flt_list = []
        if 'GlobalFilter' in original_config:
            self.filter_register._global_filter = original_config['GlobalFilter']
        if isinstance(self._config, dict):
            # this is option 1
            if self.name in self._config:
                self._config = self._config[self.name]
            # otherwise, we assume is option 2
        for key, value in self._config.items():
            if key in self._processor_parameters:
                type_: ParameterType = type(self.get_parameter(key).value)  # type: ignore # wait for answer from SO
                self.set_parameter_value(key, type_(value))  # type: ignore # no idea how to fix it, may be linked with above
            elif key == 'Filter':
                # we got a filter table!
                # it should contain one table for each model
                # we add all the names to a list for deferred initialisation
                flt_table = self._config[key]
                flt_list.extend([f'{self.name}.Filter.{model}' for model in flt_table])

        # only now, after the configuration file has been totally read, we can do the real filter initialisation.
        # This is to be sure that if there were a GlobalFilter table, this has been read.
        # The global filter region will be used as a starting point for the construction of a new filter (default
        # parameter in the from_conf class method).
        for flt_name in flt_list:
            model_name = flt_name.split('.')[-1]
            self.filter_register[model_name] = mafw.db.db_filter.Filter.from_conf(
                flt_name, original_config, original_config['GlobalFilter']
            )

    @ensure_parameter_registration
    def _overrule_kws_parameters(self) -> None:
        for key, value in self._kwargs.items():
            if key in self._processor_parameters:
                type_: ParameterType = type(self.get_parameter(key).value)  # type: ignore # wait for answer from SO
                self.set_parameter_value(key, type_(value))  # type: ignore # no idea how to fix it, may be linked with above

    def _check_method_overload(self) -> None:
        """
        Check if the user overloaded the required methods.

        Depending on the loop type, the user must overload different methods.
        This method is doing the check and if the required methods are not overloaded a warning is emitted.
        """
        methods_dict: dict[LoopType, list[str]] = {
            LoopType.WhileLoop: ['while_condition'],
            LoopType.ForLoop: ['get_items'],
        }
        required_methods: list[str] = methods_dict.get(self.loop_type, [])
        for method in required_methods:
            if getattr(type(self), method) == getattr(Processor, method):
                warnings.warn(
                    MissingOverloadedMethod(
                        '%s was not overloaded. The process execution workflow might not work.' % method
                    )
                )

    def _check_method_super(self) -> None:
        """
        Check if some specific methods are calling their super.

        For some specific methods (for example: start and finish), the user should always call their super method.
        This method verifies that the user implementation of these methods is including a super call, otherwise a
        warning is emitted to inform the user about the problem and possible misbehaviour of the processor.

        The list of methods to be verified is stored in a private class attribute
        :attr:`~._methods_to_be_checked_for_super` as a list of tuples, made by the name of the methods to be
        verified and the base class for comparison. The base class is required because Processor subclasses may be
        extending this list with methods that are not present in the base Processor. See, for example, the
        :meth:`~.GenericPlotter.patch_data_frame` that is required to have a super call, but it is not present in the
        base Processor.

        """
        for method, base in self._methods_to_be_checked_for_super:
            # first check if the user overloaded the method.
            if getattr(type(self), method) != getattr(base, method):
                # if the method is the start method, then it might be that the user decorated the class with the @database_required decorator,
                # so it looks different, but it is not
                if method == 'start':
                    sub_start_src = inspect.getsource(getattr(type(self), method))
                    base_start_src = inspect.getsource(getattr(base, method))
                    if sub_start_src == base_start_src:
                        # it is actually the same method even though the function object is different, then
                        # there is no need to check for the super_call
                        continue

                # let's check if in the overloaded method there is super calls
                super_call = f'super().{method}'
                method_object = getattr(type(self), method)

                # this is the overloaded method source code.
                method_source_code = inspect.getsource(method_object)
                # we split the whole code in lines
                code_lines = method_source_code.split('\n')
                # we remove all comments, because the user may have commented out the super
                code_lines = [line.strip() for line in code_lines if not line.strip().startswith('#')]
                # we rebuild the whole source code, without indentation and comments.
                method_source_code = '\n'.join(code_lines)

                # check if the super call is in the source. if not then emit a warning
                if super_call not in method_source_code:
                    warnings.warn(
                        MissingSuperCall(
                            'The overloaded %s is not invoking its super method. The processor might not work.' % method
                        )
                    )

    @ensure_parameter_registration
    def dump_parameter_configuration(self, option: int = 1) -> dict[str, Any]:
        """
        Dumps the processor parameter values in a dictionary.

        The snipped below explains the meaning of `option`.

        .. code-block:: python

            # option 1
            conf_dict1 = {
                'Processor': {'param1': 5, 'input_table': 'my_table'}
            }

            # option 2
            conf_dict2 = {'param1': 5, 'input_table': 'my_table'}

        :param option: Select the dictionary style. Defaults to 1.
        :type option: int, Optional
        :return: A parameter configuration dictionary.
        :rtype: dict
        """
        inner_dict = {}
        for key, value in self._processor_parameters.items():
            inner_dict[key] = value.value

        if option == 1:
            outer_dict = {self.name: inner_dict}
        elif option == 2:
            outer_dict = inner_dict
        else:
            log.warning('Unknown option %s. Using option 2' % option)
            outer_dict = inner_dict
        return outer_dict

    @ensure_parameter_registration
    def get_parameter(self, name: str) -> PassiveParameter[ParameterType]:
        """
        Gets the processor parameter named name.

        :param name: The name of the parameter.
        :type name: str
        :return: The processor parameter
        :rtype: PassiveParameter
        :raises ProcessorParameterError: If a parameter with `name` is not registered.
        """
        if name in self._processor_parameters:
            return self._processor_parameters[name]
        raise ProcessorParameterError(f'No parameter ({name}) found for {self.name}')

    @ensure_parameter_registration
    def get_parameters(self) -> dict[str, PassiveParameter[ParameterType]]:
        """
        Returns the full dictionary of registered parameters for this processor.

        Useful when dumping the parameter specification in a configuration file, for example.

        :return: The dictionary with the registered parameters.
        :rtype: dict[str, PassiveParameter[ParameterType]
        """
        return self._processor_parameters

    @ensure_parameter_registration
    def delete_parameter(self, name: str) -> None:
        """
        Deletes a processor parameter.

        :param name: The name of the parameter to be deleted.
        :type name: str
        :raises ProcessorParameterError: If a parameter with `name` is not registered.
        """
        if name in self._processor_parameters:
            del self._processor_parameters[name]
        else:
            raise ProcessorParameterError(f'No parameter ({name}) found for {self.name}')

    @ensure_parameter_registration
    def set_parameter_value(self, name: str, value: ParameterType) -> None:
        """
        Sets the value of a processor parameter.

        :param name: The name of the parameter to be deleted.
        :type name: str
        :param value: The value to be assigned to the parameter.
        :type value: ParameterType
        :raises ProcessorParameterError: If a parameter with `name` is not registered.
        """
        if name in self._processor_parameters:
            self._processor_parameters[name].value = value
        else:
            raise ProcessorParameterError(f'No parameter ({name}) found for {self.name}')

    def get_filter(self, model_name: str) -> mafw.db.db_filter.Filter:
        """
        Returns a registered :class:`~mafw.db.db_filter.Filter` via the model name.

        If a filter for the provided model_name does not exist, a KeyError is raised.

        :param model_name: The model name for which the filter will be returned.
        :type model_name: str
        :return: The registered filter
        :rtype: mafw.db.db_filter.Filter
        :raises: KeyError is a filter with the give name is not found.
        """
        return self.filter_register[model_name]

    def on_processor_status_change(self, old_status: ProcessorStatus, new_status: ProcessorStatus) -> None:
        """
        Callback invoked when the processor status is changed.

        :param old_status: The old processor status.
        :type old_status: ProcessorStatus
        :param new_status: The new processor status.
        :type new_status: ProcessorStatus
        """
        self._user_interface.change_of_processor_status(self.name, old_status, new_status)

    def on_looping_status_set(self, status: LoopingStatus) -> None:
        """
        Call back invoked when the looping status is set.

        The user can overload this method according to the needs.

        :param status: The set looping status.
        :type status: LoopingStatus
        """
        if status == LoopingStatus.Skip:
            log.warning('Skipping item %s' % self.i_item)
        elif status == LoopingStatus.Abort:
            log.error('Looping has been aborted')
        elif status == LoopingStatus.Quit:
            log.warning('Looping has been quit')

    def format_progress_message(self) -> None:
        """Customizes the progress message with information about the current item.

        The user can overload this method in order to modify the message being displayed during the process loop with
        information about the current item.

        The user can access the current value, its position in the looping cycle and the total number of items using
        :attr:`.Processor.item`, :obj:`.Processor.i_item` and :obj:`.Processor.n_item`.
        """
        pass

    @property
    def i_item(self) -> int:
        """The enumeration of the current item being processed."""
        return self._i_item

    @i_item.setter
    def i_item(self, value: int) -> None:
        self._i_item = value

    @property
    def n_item(self) -> int | None:
        """The total number of items to be processed or None for an undefined loop"""
        return self._n_item

    @n_item.setter
    def n_item(self, value: int | None) -> None:
        self._n_item = value

    @property
    def unique_name(self) -> str:
        """Returns the unique name for the processor."""
        return f'{self.name}_{self.unique_id}'

    @property
    def local_resource_acquisition(self) -> bool:
        """
        Checks if resources should be acquired locally.

        When the processor is executed in stand-alone mode, it is responsible to acquire and release its own external
        resources, but when it is executed from a ProcessorList, then is a good practice to share and distribute
        resources among the whole processor list. In this case, resources should not be acquired locally by the
        single processor, but from the parent execution context.

        :return: True if resources are to be acquired locally by the processor. False, otherwise.
        :rtype: bool
        """
        return self._resource_acquisition

    @local_resource_acquisition.setter
    def local_resource_acquisition(self, flag: bool) -> None:
        self._resource_acquisition = flag

    @property
    def database(self) -> peewee.Database:
        """
        Returns the database instance

        :return: A database object.
        :raises MissingDatabase: If the database connection has not been established.
        """
        if self._database is None:
            raise MissingDatabase('Database connection not initialized')
        return self._database

    def execute(self) -> None:
        """Execute the processor tasks.

        This method works as a dispatcher, reassigning the call to a more specific execution implementation depending
        on the :attr:`~mafw.processor.Processor.loop_type`.
        """
        dispatcher: dict[LoopType, Callable[[], None]] = {
            LoopType.SingleLoop: self._execute_single,
            LoopType.ForLoop: self._execute_for_loop,
            LoopType.WhileLoop: self._execute_while_loop,
        }
        dispatcher[self.loop_type]()

    def _execute_single(self) -> None:
        """Execute the processor in single mode.

        **Private method**. Do not overload nor invoke it directly. The :meth:`execute` method will call the
        appropriate implementation depending on the processor LoopType.
        """
        with contextlib.ExitStack() as self._resource_stack:
            self.acquire_resources()
            self.start()
            self.processor_status = ProcessorStatus.Run
            self.process()
            self.finish()

    def _execute_for_loop(self) -> None:
        """Executes the processor within a for loop.

        **Private method**. Do not overload nor invoke it directly. The :meth:`execute` method will call the
        appropriate implementation depending on the processor LoopType.
        """

        with contextlib.ExitStack() as self._resource_stack:
            self.acquire_resources()
            self.start()

            # get the input item list and filter it
            item_list = self.get_items()

            # get the total number of items.
            self.n_item = len(item_list)

            # turn the processor status to run
            self.processor_status = ProcessorStatus.Run

            # create a new task in the progress bar interface
            self._user_interface.create_task(self.unique_name, self.description, completed=0, total=self.n_item)

            # start the looping
            for self.i_item, self.item in enumerate(item_list):
                # set the looping status to Continue. The user may want to change it in the process.
                self.looping_status = LoopingStatus.Continue

                # send a message to the user interface
                self.format_progress_message()
                self._user_interface.display_progress_message(self.progress_message, self.i_item, self.n_item, 0.1)

                # wrap the execution in a timer to measure how long it took for statistical reasons.
                with Timer(suppress_message=True) as timer:
                    self.process()
                self._process_durations.append(timer.duration)

                # modify the loop depending on the looping status
                if self.looping_status == LoopingStatus.Continue:
                    self.accept_item()
                elif self.looping_status == LoopingStatus.Skip:
                    self.skip_item()
                elif self.looping_status in [LoopingStatus.Abort, LoopingStatus.Quit]:
                    break

                # update the progress bar
                self._user_interface.update_task(self.unique_name, self.i_item + 1, 1, self.n_item)
            self._user_interface.update_task(self.unique_name, completed=self.n_item, total=self.n_item)

            self.finish()

    def _execute_while_loop(self) -> None:
        """Executes the processor within a while loop.

        **Private method**. Do not overload nor invoke it directly. The :meth:`execute` method will call the
        appropriate implementation depending on the processor LoopType.
        """
        # it is a while loop, so a priori we don't know how many iterations we will have, nevertheless, we
        # can have a progress bar with 'total' set to None, so that it goes in the so-called indeterminate
        # progress. See https://rich.readthedocs.io/en/stable/progress.html#indeterminate-progress
        # we initialise n_item outside the loop, because it is possible that the user has a way to define n_item
        # and he can do it within the loop.
        self.n_item = None
        with contextlib.ExitStack() as self._resource_stack:
            self.acquire_resources()
            self.start()

            # turn the processor status to run
            self.processor_status = ProcessorStatus.Run

            self._user_interface.create_task(self.unique_name, self.description, completed=0, total=self.n_item)

            # we are ready to start the looping. For statistics, we can count the iterations.
            self.i_item = 0
            while self.while_condition():
                # set the looping status to Continue. The user may want to change it in the process method.
                self.looping_status = LoopingStatus.Continue

                # send a message to the user interface
                self.format_progress_message()
                self._user_interface.display_progress_message(
                    self.progress_message, self.i_item, self.n_item, frequency=0.1
                )

                # wrap the execution in a timer to measure how long it too for statistical reasons.
                with Timer(suppress_message=True) as timer:
                    self.process()
                self._process_durations.append(timer.duration)

                # modify the loop depending on the looping status
                if self.looping_status == LoopingStatus.Continue:
                    self.accept_item()
                elif self.looping_status == LoopingStatus.Skip:
                    self.skip_item()
                elif self.looping_status in [LoopingStatus.Abort, LoopingStatus.Quit]:
                    break

                # update the progress bar. if self.n_item is still None, then the progress bar will show indeterminate
                # progress.
                self._user_interface.update_task(self.unique_name, self.i_item + 1, 1, self.n_item)

            # now that the loop is finished, we know how many elements we processed
            if self.n_item is None:
                self.n_item = self.i_item
            self._user_interface.update_task(self.unique_name, completed=self.n_item, total=self.n_item)

            self.finish()

    def acquire_resources(self) -> None:
        """
        Acquires resources and add them to the resource stack.

        The whole body of the :meth:`execute` method is within a context structure. The idea is that if any part of
        the code inside should throw an exception that breaking the execution, we want to be sure that all stateful
        resources are properly closed.

        Since the number of resources may vary, the variable number of nested `with` statements has been replaced by
        an `ExitStack <https://docs.python.org/3/library/contextlib.html#contextlib.ExitStack>`_. Resources,
        like open files, timers, db connections, need to be added to the resource stacks in this method.

        In the case a processor is being executed within a :class:`~mafw.processor.ProcessorList`, then some resources might be shared, and
        for this reason they are not added to the stack. This selection can be done via the private
        :attr:`local_resource_acquisition`. This is normally True, meaning that the processor will handle its resources
        independently, but when the processor is executed from a :class:`~mafw.processor.ProcessorList`, this flag is automatically turned to
        False.

        If the user wants to add additional resources, he has to overload this method calling the super to preserve
        the original resources. If he wants to have shared resources among different processors executed from inside
        a processor list, he has to overload the :class:`~mafw.processor.ProcessorList` class as well.
        """
        # Both the timer and the user interface will be added to the processor resource stack only if the processor is
        # set to acquire its own resources.
        # The timer and the user interface have in-built enter and exit method.
        if self._resource_acquisition:
            self.timer = self._resource_stack.enter_context(Timer(**self._timer_parameters))
            self._resource_stack.enter_context(self._user_interface)

        # For the database it is is a bit different.
        if self._database is None and self._database_conf is None:
            # no database, nor  configuration.
            # we cannot do anything
            pass
        elif self._database is None and self._database_conf is not None:
            # no db, but we got a configuration.
            # we can make a db.
            # This processor will try to make a valid connection, and in case it succeeds, it will add the database to
            # the resource stack.
            # The database has an enter method, but it is to generate transaction.
            # We will add the database.close via the callback method.
            if 'DBConfiguration' in self._database_conf:
                conf = self._database_conf['DBConfiguration']  # type1
            else:
                conf = self._database_conf  # type2

            # guess the database type from the URL
            protocol = extract_protocol(conf.get('URL'))

            # build the connection parameter
            # in case of sqlite, we add the pragmas group as well
            connection_parameters = {}
            if protocol == 'sqlite':
                connection_parameters['pragmas'] = conf.get('pragmas', {})
            for key, value in conf.items():
                if key not in ['URL', 'pragmas']:
                    connection_parameters[key] = value

            self._database = connect(conf.get('URL'), **connection_parameters)  # type: ignore # peewee is not returning a DB
            self._resource_stack.callback(self._database.close)
            try:
                self._database.connect()
            except peewee.OperationalError as e:
                log.critical('Unable to connect to %s', self._database_conf.get('URL'))
                raise e
            database_proxy.initialize(self._database)
            self.database.create_tables(standard_tables.values())
            for table in standard_tables.values():
                table.init()

        elif self._database is not None:
            # we got a database, so very likely we are inside a processor list
            # the connection has been already set and the initialisation as well.
            # nothing else to do here.
            # do not put the database in the exit stack. who create it has also to close it.
            pass

    def start(self) -> None:
        """
        Start method.

        The user can overload this method, including all steps that should be performed at the beginning of the
        operation.

        If the user decides to overload it, it should include a call to the super method.
        """
        self.processor_status = ProcessorStatus.Start
        self._remove_orphan_files()

    def get_items(self) -> Collection[Any]:
        """
        Returns the item collections for the processor loop.

        This method must be overloaded for the processor to work. Generally, this is getting a list of rows from the
        database, or a list of files from the disk to be processed.

        :return: A collection of items for the loop
        :rtype: Collection[Any]
        """
        return []

    def while_condition(self) -> bool:
        """
        Return the while condition

        :return: True if the while loop has to continue, false otherwise.
        :rtype: bool
        """
        return False

    def process(self) -> None:
        """
        Processes the current item.

        This is the core of the Processor, where the user has to define the calculations required.
        """
        pass

    def accept_item(self) -> None:
        """
        Does post process actions on a successfully processed item.

        Within the :meth:`process`, the user left the looping status to Continue, so it means that everything looks
        good and this is the right place to perform database updates or file savings.

        .. seealso:
            Have a look at :meth:`skip_item` for what to do in case something went wrong.
        """
        pass

    def skip_item(self) -> None:
        """
        Does post process actions on a *NOT* successfully processed item.

        Within the :meth:`process`, the user set the looping status to Skip, so it means that something went wrong
        and here corrective actions can be taken if needed.

        .. seealso:
            Have a look at :meth:`accept_item` for what to do in case everything was OK.
        """
        pass

    def finish(self) -> None:
        """
        Concludes the execution.

        The user can reimplement this method if there are some conclusive tasks that must be achieved.
        Always include a call to super().
        """
        self.processor_status = ProcessorStatus.Finish
        if self.looping_status == LoopingStatus.Abort:
            self.processor_exit_status = ProcessorExitStatus.Aborted
        self.print_process_statistics()

    def print_process_statistics(self) -> None:
        """
        Print the process statistics.

        A utility method to display the fastest, the slowest and the average timing required to process on a single
        item. This is particularly useful when the looping processor is part of a ProcessorList.
        """
        if len(self._process_durations):
            log.info('[cyan] Processed %s items.' % len(self._process_durations))
            log.info(
                '[cyan] Fastest item process duration: %s '
                % pretty_format_duration(min(self._process_durations), n_digits=3)
            )
            log.info(
                '[cyan] Slowest item process duration: %s '
                % pretty_format_duration(max(self._process_durations), n_digits=3)
            )
            log.info(
                '[cyan] Average item process duration: %s '
                % pretty_format_duration((sum(self._process_durations) / len(self._process_durations)), n_digits=3)
            )
            log.info(
                '[cyan] Total process duration: %s' % pretty_format_duration(sum(self._process_durations), n_digits=3)
            )

    def _remove_orphan_files(self) -> None:
        """
        Remove orphan files.

        If a connection to the database is available, then the OrphanFile standard table is queried for all its entries,
        and all the files are then removed.

        The user can turn off this behaviour by switching the :attr:`~mafw.processor.Processor.remove_orphan_files` to False.

        """
        if self._database is None or self.remove_orphan_files is False:
            # no database connection or no wish to remove orphan files, it does not make sense to continue
            return

        # noinspection PyPep8Naming
        OrphanFile = cast(PeeweeModelWithMeta, standard_tables['OrphanFile'])

        if OrphanFile._meta.table_name not in self._database.get_tables():
            log.warning('OrphanFile table not found in DB. Please verify database integrity')
            return

        orphan_files = OrphanFile.select().execute()
        if len(orphan_files) != 0:
            msg = f'[yellow]Pruning orphan files ({len(orphan_files)})...'
            log.info(msg)
            for orphan in orphan_files:
                # filenames is a list of files:
                for f in orphan.filenames:
                    f.unlink(missing_ok=True)
            OrphanFile.delete().execute()


class ProcessorList(list[Union['Processor', 'ProcessorList']]):
    """
    A list like collection of processors.

    ProcessorList is a subclass of list containing only Processor subclasses or other ProcessorList.

    An attempt to add an element that is not a Processor or a ProcessorList will raise a TypeError.

    Along with an iterable of processors, a new processor list can be built using the following parameters.
    """

    def __init__(
        self,
        *args: Processor | ProcessorList,
        name: str | None = None,
        description: str | None = None,
        timer: Timer | None = None,
        timer_params: dict[str, Any] | None = None,
        user_interface: UserInterfaceBase | None = None,
        database: Database | None = None,
        database_conf: dict[str, Any] | None = None,
    ):
        """
        Constructor parameters:

        :param name: The name of the processor list. Defaults to ProcessorList.
        :type name: str, Optional
        :param description: An optional short description. Default to ProcessorList.
        :type description: str, Optional
        :param timer: The timer object. If None is provided, a new one will be created. Defaults to None.
        :type timer: Timer, Optional
        :param timer_params: A dictionary of parameter to build the timer object. Defaults to None.
        :type timer_params: dict, Optional
        :param user_interface: A user interface. Defaults to None
        :type user_interface: UserInterfaceBase, Optional
        :param database: A database instance. Defaults to None.
        :type database: Database, Optional
        :param database_conf: Configuration for the database. Default to None.
        :type database_conf: dict, Optional
        """

        # validate_items takes a tuple of processors, that's why we don't unpack args.
        super().__init__(self.validate_items(args))
        self._name = name or self.__class__.__name__
        self.description = description or self._name

        self.timer = timer
        self.timer_params = timer_params or {}
        self._user_interface = user_interface or ConsoleInterface()

        self._resource_stack: contextlib.ExitStack
        self._processor_exit_status: ProcessorExitStatus = ProcessorExitStatus.Successful

        # database stuff
        self._database: peewee.Database | None = database
        self._database_conf: dict[str, Any] | None = validate_database_conf(database_conf)

    def __setitem__(  # type: ignore[override]
        self,
        __index: SupportsIndex,
        __object: Processor | ProcessorList,
    ) -> None:
        super().__setitem__(__index, self.validate_item(__object))

    def insert(self, __index: SupportsIndex, __object: Processor | ProcessorList) -> None:
        """Adds a new processor at the specified index."""
        super().insert(__index, self.validate_item(__object))

    def append(self, __object: Processor | ProcessorList) -> None:
        """Appends a new processor at the end of the list."""
        super().append(self.validate_item(__object))

    def extend(self, __iterable: Iterable[Processor | ProcessorList]) -> None:
        """Extends the processor list with a list of processors."""
        if isinstance(__iterable, type(self)):
            super().extend(__iterable)
        else:
            super().extend([self.validate_item(item) for item in __iterable])

    @staticmethod
    def validate_item(item: Processor | ProcessorList) -> Processor | ProcessorList:
        """Validates the item being added."""
        if isinstance(item, Processor):
            item.local_resource_acquisition = False
            return item
        elif isinstance(item, ProcessorList):
            item.timer_params = dict(suppress_message=True)
            return item
        else:
            raise TypeError(f'Expected Processor or ProcessorList, got {type(item).__name__}')

    @staticmethod
    def validate_items(items: tuple[Processor | ProcessorList, ...] = ()) -> tuple[Processor | ProcessorList, ...]:
        """Validates a tuple of items being added."""
        if not items:
            return tuple()
        return tuple([ProcessorList.validate_item(item) for item in items if item is not None])

    @property
    def name(self) -> str:
        """
        The name of the processor list

        :return: The name of the processor list
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def processor_exit_status(self) -> ProcessorExitStatus:
        """
        The processor exit status.

        It refers to the whole processor list execution.
        """
        return self._processor_exit_status

    @processor_exit_status.setter
    def processor_exit_status(self, status: ProcessorExitStatus) -> None:
        self._processor_exit_status = status

    @property
    def database(self) -> peewee.Database:
        """
        Returns the database instance

        :return: A database instance
        :raises MissingDatabase: if a database connection is missing.
        """
        if self._database is None:
            raise MissingDatabase('Database connection not initialized')
        return self._database

    def execute(self) -> ProcessorExitStatus:
        """
        Execute the list of processors.

        Similarly to the :class:`Processor`, ProcessorList can be executed. In simple words, the execute
        method of each processor in the list is called exactly in the same sequence as they were added.
        """
        with contextlib.ExitStack() as self._resource_stack:
            self.acquire_resources()
            self._user_interface.create_task(self.name, self.description, completed=0, increment=0, total=len(self))
            for i, item in enumerate(self):
                if isinstance(item, Processor):
                    log.info('Executing [red]%s[/red] processor' % item.name)
                else:
                    log.info('Executing [red]%s[/red] processor list' % item.name)
                self.distribute_resources(item)
                item.execute()
                self._user_interface.update_task(self.name, i, 1, len(self))
                self._processor_exit_status = item.processor_exit_status
                if self._processor_exit_status == ProcessorExitStatus.Aborted:
                    msg = 'Processor %s caused the processor list to abort' % item.name
                    log.error(msg)
                    raise AbortProcessorException(msg)
            self._user_interface.update_task(self.name, completed=len(self), total=len(self))
        return self._processor_exit_status

    def acquire_resources(self) -> None:
        """Acquires external resources."""
        # The strategy is similar to the one for processor. if we do get resources already active (not None) then we use
        # them, otherwise, we create them and we add them to the resource stack.
        if self.timer is None:
            self.timer = self._resource_stack.enter_context(Timer(**self.timer_params))
        self._resource_stack.enter_context(self._user_interface)
        if self._database is None and self._database_conf is None:
            # no database, nor  configuration.
            # we cannot do anything
            pass
        elif self._database is None and self._database_conf is not None:
            # no db, but we got a configuration.
            # we can make a db
            if 'DBConfiguration' in self._database_conf:
                conf = self._database_conf['DBConfiguration']  # type1
            else:
                conf = self._database_conf  # type2

            # guess the database type from the URL
            protocol = extract_protocol(conf.get('URL'))

            # build the connection parameter
            # in case of sqlite, we add the pragmas group as well
            connection_parameters = {}
            if protocol == 'sqlite':
                connection_parameters['pragmas'] = conf.get('pragmas', {})
            for key, value in conf.items():
                if key not in ['URL', 'pragmas']:
                    connection_parameters[key] = value

            self._database = connect(conf.get('URL'), **connection_parameters)  # type: ignore # peewee is not returning a DB
            try:
                self._database.connect()
                self._resource_stack.callback(self._database.close)
            except peewee.OperationalError as e:
                log.critical('Unable to connect to %s', self._database_conf.get('URL'))
                raise e
            database_proxy.initialize(self._database)
            self.database.create_tables(standard_tables.values())
            for table in standard_tables.values():
                table.init()
        elif self._database is not None:
            # we got a database, so very likely we are inside a processor list
            # the connection has been already set and the initialisation as well.
            # nothing else to do here.
            pass

    def distribute_resources(self, processor: Processor | Self) -> None:
        """Distributes the external resources to the items in the list."""
        processor.timer = self.timer
        processor._user_interface = self._user_interface
        processor._database = self._database
