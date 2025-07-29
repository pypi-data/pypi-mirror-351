"""
The module provides some general decorator utilities that are used in several parts of the code, and that can be
reused by the user community.
"""

import functools
import typing
import warnings
from importlib.util import find_spec
from typing import Any

from mafw.enumerators import LoopType
from mafw.mafw_errors import MissingDatabase, MissingOptionalDependency
from mafw.processor import Processor


@typing.no_type_check  # no idea how to fix it
def singleton(cls):
    """Make a class a Singleton class (only one instance)"""

    @functools.wraps(cls)
    def wrapper_singleton(*args: Any, **kwargs: Any):
        if wrapper_singleton.instance is None:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance

    wrapper_singleton.instance = None
    return wrapper_singleton


@typing.no_type_check
def database_required(cls):
    """Modify the processor start method to check if a database object exists.

    This decorator must be applied to processors requiring a database connection.

    :param cls: A Processor class.
    """
    orig_start = cls.start

    @functools.wraps(cls.start)
    def _start(self) -> None:
        if self._database is None:
            raise MissingDatabase(f'{self.name} requires an active database.')
        orig_start(self)

    cls.start = _start

    return cls


@typing.no_type_check
def orphan_protector(cls):
    """
    A class decorator to modify the init method of a Processor so that the remove_orphan_files is set to False and
    no orphan files will be removed.
    """
    old_init = cls.__init__

    @functools.wraps(cls.__init__)
    def new_init(self, *args, **kwargs):
        old_init(self, *args, remove_orphan_files=False, **kwargs)

    cls.__init__ = new_init
    return cls


@typing.no_type_check
def execution_workflow(loop_type: LoopType | str = LoopType.ForLoop):
    """
    A decorator factory for the definition of the looping strategy.

    This decorator factory must be applied to Processor subclasses to modify their value of loop_type in order to
    change the execution workflow.

    See :func:`single_loop`, :func:`for_loop` and :func:`while_loop` decorator shortcuts.

    :param loop_type: The type of execution workflow requested for the decorated class. Defaults to LoopType.ForLoop.
    :type loop_type: LoopType | str, Optional
    """

    def dec(cls):
        """The class decorator."""
        old_init = cls.__init__

        @functools.wraps(cls.__init__)
        def new_init(self, *args, **kwargs):
            """The modified Processor init"""
            old_init(self, *args, looper=loop_type, **kwargs)

        cls.__init__ = new_init

        return cls

    return dec


single_loop = execution_workflow(LoopType.SingleLoop)
"""A decorator shortcut to define a single execution processor."""

for_loop = execution_workflow(LoopType.ForLoop)
"""A decorator shortcut to define a for loop execution processor."""

while_loop = execution_workflow(LoopType.WhileLoop)
"""A decorator shortcut to define a while loop execution processor."""


@typing.no_type_check
def depends_on_optional(module_name: str, raise_ex: bool = False, warn: bool = True):
    """
    Function decorator to check if module_name is available.

    If module_name is found, then returns the wrapped function. If not, its behaviour depends on the raise_ex and
    warn_only values. If raise_ex is True, then an ImportError exception is raised. If it is False and warn is
    True, then a warning message is displayed but no exception is raised. If they are both False, then function is
    silently skipped.

    If raise_ex is True, the value of `warn` is not taken into account.

    **Typical usage**

    The user should decorate functions or class methods when they cannot be executed without the optional library.
    In the specific case of Processor subclass, where the class itself can be created also without the missing
    library, but it is required somewhere in the processor execution, then the user is suggested to decorate the
    execute method with this decorator.

    Here below a code snippet demonstrating the use.

    .. code-block:: python
        :caption: Use of the decorator with class methods.
        :linenos:
        :name: func_deco

        # other import statements...
        # ...
        try:
            import missing_lib
        except:
            # do not complain if not found. The decorator will take care of informing the user in case.
            missing_lib = None

        class MyClass(Processor):
            def __init__(self, parsed_args: argparse.Namespace, n: int, *args, **kwargs):
                # the class init does not require the missing library
                super().__init__(parsed_args, *args, **kwargs)
                self.n = n

            @depends_on_optional('missing_lib', raise_ex=False, warn=True)
            def execute(self):
                super().execute()

            def process(self):
                log.info(\'[red]I am calculating\')
                log.info(self.n**2)
                time.sleep(0.5)

        def main():
            try:
                arg_parser = get_parser()
                args = arg_parser.parse_args()
                logging_helper.set_logger(args)

                # create an instance of MyClass
                mc = MyClass(args, 12)
                # execute it!
                mc.execute()
                #
                # output:
                #
                # WARNING  Optional dependency missing_lib not found (MyClass.execute)

                # create a ProcessorList
                mp = ProcessorList(name='Multi')
                mp.append(MyClass(args, 12))
                mp.execute()
                #
                # output:
                #
                # INFO     Executing MyClass processor
                # WARNING  Optional dependency missing_lib not found (MyClass.execute)
                # Multi processor list execution ----------------------------------- 100% 0:00:00
                # INFO     Total execution time:

            except ImportError:
                # since the raise_ex flag of the decorator is set to False, there won't be an exception
                log.warning('Whole processing stopped because of missing optional dep')

        if __name__ == '__main__':
            main()

    If also the class __init__ method requires access to the missing_lib, then the user has to use the class
    decorator :func:`~.processor_depends_on_optional`.

    :param module_name: The optional module(s) from which the function depends on. A \";\" separated list of modules can
        also be provided.
    :type module_name: str
    :param raise_ex: Flag to raise an exception if module_name is not found, defaults to False.
    :type raise_ex: bool, Optional
    :param warn: Flag to display a warning message if module_name is not found, default to True.
    :type warn: bool, Optional
    :return: The wrapped function
    :rtype: Callable
    :raise ImportError: if module_name is not found and raise_ex is True.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            all_mods_found = all([find_spec(mod.strip()) is not None for mod in module_name.split(';')])
            if not all_mods_found:
                msg = f'Optional dependency {module_name} not found ({func.__qualname__})'
                if raise_ex:
                    raise ImportError(msg)
                else:
                    if warn:
                        warnings.warn(MissingOptionalDependency(msg), stacklevel=2)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


@typing.no_type_check
def processor_depends_on_optional(module_name: str, raise_ex: bool = False, warn: bool = True):
    """
    Class decorator factory to check if module module_name is available.

    It checks if all the optional modules listed in `module_name` separated by a ';' can be found.

    If all modules are found, then the class is returned as it is.

    If at least one module is not found:
     - and raise_ex is True, an ImportError exception is raised and the user is responsible to deal with it.
     - if raise_ex is False, instead of returning the class, the :class:`~.Processor` is returned.
     - depending on the value of warn, the user will be informed with a warning message or not.

    **Typical usage**

    The user should decorate Processor subclasses everytime the optional module is required in their __init__ method.
    Should the check on the optional module have a positive outcome, then the Processor subclass is returned.
    Otherwise, if raise_ex is False, an instance of the base :py:class:`~.Processor` is returned. In
    this way, the returned class can still be executed without breaking the execution scheme but of course, without
    producing any output.

    Should be possible to run the __init__ method of the class without the missing library, then the user can also
    follow the approach described in this other :ref:`example <func_deco>`.

    :param module_name: The optional module(s) from which the class depends on. A \";\" separated list of modules can
        also be provided.
    :type module_name: str
    :param raise_ex: Flag to raise an exception if module_name not found, defaults to False.
    :type raise_ex: bool, Optional
    :param warn: Flag to display a warning message if module_name is not found, defaults to True.
    :type warn: bool, Optional
    :return: The wrapped processor.
    :rtype: type(Processor)
    :raise ImportError: if module_name is not found and raise_ex is True.
    """

    def decorator(cls):
        """
        The class decorator.

        It checks if all the modules provided by the decorator factory are available on the systems.
        If yes, then it simply returns `cls`. If no, it returns a subclass of the :class:`~.Processor`
        after all the introspection properties have been taken from `cls`.

        :param cls: The class being decorated.
        :type cls: type(Processor)
        :return: The decorated class, either cls or a subclass of  :class:`~autorad.processor.Processor`.
        :rtype: type(Processor)
        """

        def class_wrapper(klass):
            """
            Copy introspection properties from cls to klass.

            :param klass: The class to be modified.
            :type klass: class.
            :return: The modified class.
            :rtype: class.
            """
            klass.__module__ = cls.__module__
            klass.__name__ = f'{cls.__name__} (Missing {module_name})'
            klass.__qualname__ = cls.__qualname__
            klass.__annotations__ = cls.__annotations__
            klass.__doc__ = cls.__doc__
            return klass

        all_mods_found = all([find_spec(mod.strip()) is not None for mod in module_name.split(';')])
        if not all_mods_found:
            msg = f'Optional dependency {module_name} not found ({cls.__qualname__})'
            if raise_ex:
                raise ImportError(msg)
            else:
                if warn:
                    warnings.warn(MissingOptionalDependency(msg), stacklevel=2)

                # we subclass the basic processor.
                # this is needed because we want to wrap the returned class with the introspection properties of cls
                # w/o modifying processor.Processor.
                @single_loop
                class NewClass(Processor):
                    pass

                # the class wrapper is copying introspection properties from the cls to the NewClass
                new_class = class_wrapper(NewClass)

        else:
            new_class = cls
        return new_class

    return decorator
