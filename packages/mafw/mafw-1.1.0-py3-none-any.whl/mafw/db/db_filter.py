"""
The module provides the capability to filter model classes with information taken from the steering file.
"""

import operator
import warnings
from collections import UserDict
from copy import copy
from functools import reduce
from typing import Any, Self, cast

import peewee
from peewee import Model


class Filter:
    r"""
    Class to filter rows from a model.

    The filter object can be used to generate a where clause to be applied to Model.select().

    The construction of a Filter is normally done via a configuration file using the :meth:`from_conf` class method.
    The name of the filter is playing a key role in this. If it follows a dot structure like:

        *ProcessorName.Filter.ModelName*

    then the corresponding table from the TOML configuration object will be used.

    For each processor, there might be many Filters, up to one for each Model used to get the input list. If a
    processor is joining together three Models when performing the input select, there will be up to three Filters
    collaborating on making the selection.

    The filter configuration can contain the following key, value pair:

        - key / string pairs, where the key is the name of a field in the corresponding Model

        - key / numeric pairs

        - key / arrays

    All fields from the configuration file will be added to the instance namespace, thus accessible with the dot
    notation. Moreover, the field names and their filter value will be added to a private dictionary to simplify the
    generation of the filter SQL code.

    The user can use the filter object to store selection criteria. He can construct queries using the filter
    contents in the same way as he could use processor parameters.

    If he wants to automatically generate valid filtering expression, he can use the :meth:`filter` method. In order
    for this to work, the Filter object be :meth:`bound <bind>` to a Model. Without this binding the Filter will not
    be able to automatically generate expressions.

    For each field in the filter, one condition will be generated according to the following scheme:

    =================   =================   ==================
    Filter field type   Logical operation      Example
    =================   =================   ==================
    Numeric, boolean        ==               Field == 3.14
    String                 GLOB             Field GLOB '\*ree'
    List                   IN               Field IN [1, 2, 3]
    =================   =================   ==================

    All conditions will be joined with a AND logic.

    Consider the following example:

    .. code-block:: python
        :linenos:

        class MeasModel(MAFwBaseModel):
            meas_id = AutoField(primary_key=True)
            sample_name = TextField()
            successful = BooleanField()

        flt = Filter('MyProcessor.Filter.MyModel', sample_name='sample_00*',
                    meas_id=[1,2,3], successful=True)
        flt.bind(MeasModel)

        filter_select_manual = MeasModel.select().where((MeasModel.meas_id.in_(flt.meas_id) &
                                                        (MeasModel.sample_name % flt.sample_name) &
                                                        (MeasModel.successful == flt.successful))

        filter_select_auto = MeasModel.select().where(flt.filter())

    At line 6, we created a Filter and at 8 we bind it to our Model class. The two select at 10 and 14 are actually
    identical.

    """

    def __init__(self, name: str, **kwargs: Any) -> None:
        """
        Constructor parameters:

        :param name: The name of the filter. It should be in dotted format to facilitate the configuration via the
            steering file.
        :type name: str
        :param kwargs: Keyword parameters corresponding to fields and filter values.
        """
        self.name = name
        self.model_name = name.split('.')[-1]
        self.model: type[Model] | None = None
        self._model_bound: bool = False
        self._fields = {}
        for k, v in kwargs.items():
            self._fields[k] = v
            setattr(self, k, v)

    def bind(self, model: type[Model] | None = None) -> None:
        """
        Connects a filter to a Model class.

        If no model is provided, the method will try to bind a class from with global dictionary with a name matching
        the model name used during the Filter configuration. It only works when the Model is defined as global.

        :param model: Model to be bound. Defaults to None
        :type model: Model, Optional
        """
        if model is None:
            if self.model_name in globals():
                self.model = globals()[self.model_name]
                self._model_bound = True
        else:
            self.model = model
            self._model_bound = True

    @property
    def is_bound(self) -> bool:
        """Returns true if the Filter has been bound to a Model"""
        return self._model_bound

    def get_field(self, key: str) -> Any:
        """
        Gets a field by name.

        :param key: The name of the field.
        :type key: str
        :return: The value of the field.
        :rtype: Any
        :raises KeyError: if the requested field does not exist.
        """
        return self._fields[key]

    def set_field(self, key: str, value: Any) -> None:
        """
        Sets the value of a field by name

        :param key: The name of the field.
        :type key: str
        :param value: The value of the field.
        :type value: Any
        """
        self._fields[key] = value

    @property
    def field_names(self) -> list[str]:
        """The list of field names."""
        return list(self._fields.keys())

    @classmethod
    def from_conf(cls, name: str, conf: dict[str, Any], default: dict[str, Any] | None = None) -> Self:
        """
        Builds a Filter object from a steering file dictionary.

        If the name is in dotted notation, then this should be corresponding to the table in the configuration file.
        If a default configuration is provided, this will be used as a starting point for the filter, and it will be
        updated by the actual configuration in ``conf``.

        In normal use, you would provide the specific configuration via the conf parameter and the global filter
        configuration as default.

        See details in the :class:`class documentation <Filter>`

        :param name: The name of the filter in dotted notation.
        :type name: str
        :param conf: The configuration dictionary.
        :type conf: dict
        :param default: Default configuration dictionary
        :type default: dict
        :return: A Filter object
        :rtype: Filter
        """
        param = default or {}

        # split the name from dotted notation
        # ProcessorName.ModelName.Filter
        names = name.split('.')
        if len(names) == 3 and names[1] == 'Filter':
            proc_name, _, model_name = names
            if proc_name in conf and 'Filter' in conf[proc_name] and model_name in conf[proc_name]['Filter']:
                param.update(copy(conf[proc_name]['Filter'][model_name]))

        # if the name is not in the expected dotted notation, then param will be the default, that very likely means
        # the global filter configuration.
        return cls(name, **param)

    def filter(self) -> peewee.Expression | bool:
        """
        Generates a filtering expression logically ANDing all filtering fields.

        See details in the :class:`class documentation <Filter>`

        :return: The filtering expression.
        :rtype: peewee.Expression
        """
        if not self.is_bound:
            warnings.warn('Unable to generate the filter. Did you bind the filter to the model?')
            return True
        else:
            expression_list = []
            for field, value in self._fields.items():
                if hasattr(self.model, field):
                    if isinstance(value, (int, float, bool)):
                        expression_list.append(getattr(self.model, field) == value)
                    elif isinstance(value, str):
                        expression_list.append(getattr(self.model, field) % value)
                    elif isinstance(value, list):
                        expression_list.append(getattr(self.model, field).in_(value))
            # if len(expression_list) == 0:
            #     return True
            return reduce(operator.and_, expression_list, True)


class FilterRegister(UserDict[str, Filter]):
    """
    A special dictionary to store all :class:`Filters <mafw.db.db_filter.Filter>` in a processors.

    It contains a publicly accessible dictionary with the configuration of each Filter using the Model name as
    keyword.

    It contains a private dictionary with the global filter configuration as well.
    The global filter is not directly accessible, but only some of its members will be exposed via properties.
    In particular, the new_only flag that is relevant only at the Processor level can be accessed directly using the
    :attr:`new_only`. If not specified in the configuration file, the new_only is by default True.
    """

    def __init__(self, data: dict[str, Filter] | None = None, /, **kwargs: Any) -> None:
        """
        Constructor parameters:

        :param data: Initial data
        :type data: dict
        :param kwargs: Keywords arguments
        """
        self._global_filter: dict[str, Any] = {}
        super().__init__(data, **kwargs)

    @property
    def new_only(self) -> bool:
        """
        The new only flag.

        :return: True, if only new items, not already in the output database table must be processed.
        :rtype: bool
        """
        return cast(bool, self._global_filter.get('new_only', True))

    @new_only.setter
    def new_only(self, v: bool) -> None:
        self._global_filter['new_only'] = v

    def __setitem__(self, key: str, value: Filter) -> None:
        """
        Set a new value at key.

        If value is not a Filter, then it will be automatically and silently discarded.

        :param key: Dictionary key. Normally the name of the model linked to the filter.
        :type key: str
        :param value: The Filter.
        :type value: Filter
        """
        if not isinstance(value, Filter):
            return
        super().__setitem__(key, value)

    def bind_all(self, models: list[type[Model]] | dict[str, type[Model]]) -> None:
        """
        Binds all filters to their models.

        The ``models`` list or dictionary should contain a valid model for all the Filter in the registry.
        In the case of a dictionary, the key value should be the model name.

        If the user provides a model for which there is no corresponding filter in the register, then a new filter
        for that model is created using the GlobalFilter default.

        This can happen if the user did not provide a specific table for the Processor/Model, but simply put all
        filtering conditions in the GlobalFilter table. Even though, this behaviour is allowed and working,
        it may result in unexpected results. Also listing more than needed models in the input list can be dangerous
        because they will anyhow use the default filters.

        :param models: List or dictionary of a databank of Models from which the Filter can be bound.
        :type models:  list[type(Model)] | dict[str,type(Model)]
        """
        if isinstance(models, list):
            models = {m.__name__: m for m in models}

        # check, if we have a filter for each listed models, if not create one using the default configuration.
        for model_name in models.keys():
            if model_name not in self.data:
                self.data[model_name] = Filter.from_conf(f'{model_name}', conf={}, default=self._global_filter)

        for k, v in self.data.items():
            if k in self.data:
                v.bind(models[k])
            else:
                v.bind()

    def filter_all(self):  # type: ignore[no-untyped-def]
        """
        Generates a where clause ANDing all filters.

        If one Filter is not bound, then True is returned.
        """
        filter_list = [flt.filter() for flt in self.data.values() if flt.is_bound]
        return reduce(operator.and_, filter_list, True)
