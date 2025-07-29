"""
The module provides functionality to MAFw to interface to a DB.
"""

import warnings
from typing import Any, Iterable, cast

from peewee import DatabaseProxy, ModelInsert

# noinspection PyUnresolvedReferences
from playhouse.signals import Model

from mafw.db.db_types import PeeweeModelWithMeta
from mafw.db.trigger import Trigger
from mafw.mafw_errors import MAFwException, UnsupportedDatabaseError

database_proxy = DatabaseProxy()
"""This is a placeholder for the real database object that will be known only at run time"""


class MAFwBaseModelDoesNotExist(MAFwException):
    """Raised when the base model class is not existing."""


class MAFwBaseModel(Model):
    """The base model for the MAFw library.

    Every model class (table) that the user wants to interface must inherit from this base.
    """

    @classmethod
    def triggers(cls) -> list[Trigger]:
        """
        Returns an iterable of :class:`~mafw.db.trigger.Trigger` objects to create upon table creation.

        The user must overload this returning all the triggers that must be created along with this class.
        """
        return []

    # noinspection PyUnresolvedReferences
    @classmethod
    def create_table(cls, safe: bool = True, **options: Any) -> None:
        """
        Create the table in the underlying DB and all the related trigger as well.

        If the creation of a trigger fails, then the whole table dropped, and the original exception is re-raised.

        .. warning::

            Trigger creation has been extensively tested with :link:`SQLite`, but not with the other database implementation.
            Please report any malfunction.

        :param safe: Flag to add an IF NOT EXISTS to the creation statement. Defaults to True.
        :type safe: bool, Optional
        :param options: Additional options passed to the super method.
        """
        super().create_table(safe, **options)

        # this is just use to make mypy happy.
        meta_cls = cast(PeeweeModelWithMeta, cls)

        # Get the database instance, it is used for trigger creation
        db = meta_cls._meta.database

        triggers_list = cls.triggers()
        if len(triggers_list):
            # Create tables with appropriate error handling
            try:
                for trigger in triggers_list:
                    trigger.set_database(db)
                    try:
                        db.execute_sql(trigger.create())
                    except UnsupportedDatabaseError as e:
                        warnings.warn(f'Skipping unsupported trigger {trigger.trigger_name}: {str(e)}')
                    except Exception:
                        raise
            except:
                # If an error occurs, drop the table and any created triggers
                meta_cls._meta.database.drop_tables([cls], safe=safe)
                for trigger in triggers_list:
                    try:
                        db.execute_sql(trigger.drop(True))
                    except Exception:
                        pass  # Ignore errors when dropping triggers during cleanup
                raise

    # noinspection PyProtectedMember
    @classmethod
    def std_upsert(cls, __data: dict[str, Any] | None = None, **mapping: Any) -> ModelInsert:
        """
        Perform a so-called standard upsert.

        An upsert statement is not part of the standard SQL and different databases have different ways to implement it.
        This method will work for modern versions of :link:`sqlite` and :link:`postgreSQL`.
        Here is a `detailed explanation for SQLite <https://www.sqlite.org/lang_upsert.html>`_.

        An upsert is a statement in which we try to insert some data in a table where there are some constraints.
        If one constraint is failing, then instead of inserting a new row, we will try to update the existing row
        causing the constraint violation.

        A standard upsert, in the naming convention of MAFw, is setting the conflict cause to the primary key with all
        other fields being updated. In other words, the database will try to insert the data provided in the table, but
        if the primary key already exists, then all other fields will be updated.

        This method is equivalent to the following:

        .. code-block:: python

            class Sample(MAFwBaseModel):
                sample_id = AutoField(
                    primary_key=True,
                    help_text='The sample id primary key',
                )
                sample_name = TextField(help_text='The sample name')


            (
                Sample.insert(sample_id=1, sample_name='my_sample')
                .on_conflict(
                    preserve=[Sample.sample_name]
                )  # use the value we would have inserted
                .execute()
            )

        :param __data: A dictionary containing the key/value pair for the insert. The key is the column name.
            Defaults to None
        :type __data: dict, Optional
        :param mapping: Keyword arguments representing the value to be inserted.
        """
        # this is used just to make mypy happy.
        # cls and meta_cls are exactly the same thing
        meta_cls = cast(PeeweeModelWithMeta, cls)

        if meta_cls._meta.composite_key:
            conflict_target = [meta_cls._meta.fields[n] for n in meta_cls._meta.primary_key.field_names]
        else:
            conflict_target = [meta_cls._meta.primary_key]

        conflict_target_names = [f.name for f in conflict_target]
        preserve = [f for n, f in meta_cls._meta.fields.items() if n not in conflict_target_names]
        return cast(
            ModelInsert, cls.insert(__data, **mapping).on_conflict(conflict_target=conflict_target, preserve=preserve)
        )

    # noinspection PyProtectedMember
    @classmethod
    def std_upsert_many(cls, rows: Iterable[Any], fields: list[str] | None = None) -> ModelInsert:
        """
        Perform a standard upsert with many rows.

        .. seealso::

            Read the :meth:`std_upsert` documentation for an explanation of this method.

        :param rows: A list with the rows to be inserted. Each item can be a dictionary or a tuple of values. If a
            tuple is provided, then the `fields` must be provided.
        :type rows: Iterable
        :param fields: A list of field names. Defaults to None.
        :type fields: list[str], Optional
        """
        # this is used just to make mypy happy.
        # cls and meta_cls are exactly the same thing
        meta_cls = cast(PeeweeModelWithMeta, cls)

        if meta_cls._meta.composite_key:
            conflict_target = [meta_cls._meta.fields[n] for n in meta_cls._meta.primary_key.field_names]
        else:
            conflict_target = [meta_cls._meta.primary_key]

        conflict_target_names = [f.name for f in conflict_target]
        preserve = [f for n, f in meta_cls._meta.fields.items() if n not in conflict_target_names]
        return cast(
            ModelInsert,
            (
                cls.insert_many(rows, fields).on_conflict(
                    conflict_target=conflict_target,
                    preserve=preserve,
                )
            ),
        )

    class Meta:
        """The metadata container for the Model class"""

        database = database_proxy
        """The reference database. A proxy is used as a placeholder that will be automatically replaced by the real 
        instance of the database at runtime."""

        legacy_table_names = False
        """
        Set the default table name as the snake case of the Model camel case name.
        
        So for example, a model named ThisIsMyTable will corresponds to a database table named this_is_my_table.
        """
