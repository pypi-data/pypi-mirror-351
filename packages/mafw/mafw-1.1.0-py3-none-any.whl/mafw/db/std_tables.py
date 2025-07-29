"""
Module provides standard tables that are included in all database created by MAFw processor.

Standard tables are automatically created and initialized by a :class:`~mafw.processor.Processor` or a
:class:`~mafw.processor.ProcessorList` when opening a database connection.

This means that if a processor receives a valid database object, then it will suppose that the connection was already
opened somewhere else (either from a ProcessorList or a third party) and thus it is not creating the standard tables.

If a processor is constructed using a database configuration dictionary, then it will first try to open a connection
to the DB, then creating all standard tables and finally executing their :class:`StandardTable.init` method. The same
apply for the Processor list.

In other words, object responsible to open the database connection is taking care also of creating the standard
tables and of initializing them. If the user opens the connection and passes it to a Processor or ProcessorList,
then the user is responsible to create the standard tables and to initialize them.

All standard tables must derive from the :class:`StandardTable` to have the same interface for the
initialization.

Users can create their own standard tables and export them as a pluggable object using the same approach as for custom
processors. An example is provided in the :ref:`documentation <my_std_tables.py>`.

"""

from typing import cast

import peewee
from peewee import AutoField, BooleanField, CharField, TextField

from mafw.db.db_model import MAFwBaseModel
from mafw.db.db_types import PeeweeModelWithMeta
from mafw.db.fields import FileChecksumField, FileNameListField
from mafw.db.trigger import Trigger, TriggerAction, TriggerWhen


class StandardTable(MAFwBaseModel):
    """A base class for tables that are generated automatically by the MAFw processor."""

    @classmethod
    def init(cls) -> None:
        """The user must overload this method, if he wants some specific operations to be performed on the model
        everytime the database is connected."""
        pass


class StandardTableDoesNotExist(Exception):
    """An exception raised when trying to access a not existing table."""


class TriggerStatus(StandardTable):
    """A Model for the trigger status"""

    trigger_type_id = AutoField(primary_key=True, help_text='Primary key')
    trigger_type = TextField(
        help_text='You can use it to specify the type (DELETE/INSERT/UPDATE) or the name of a specific trigger'
    )
    status = BooleanField(default=True, help_text='False (0) = disable / True (1) = enable')

    # noinspection PyProtectedMember
    @classmethod
    def init(cls) -> None:
        """Resets all triggers to enable when the database connection is opened."""
        data = [
            dict(trigger_type_id=1, trigger_type='DELETE', status=True),
            dict(trigger_type_id=2, trigger_type='INSERT', status=True),
            dict(trigger_type_id=3, trigger_type='UPDATE', status=True),
            dict(trigger_type_id=4, trigger_type='DELETE_FILES', status=True),
        ]

        # this is used just to make mypy happy
        # cls and meta_cls are exactly the same thing
        meta_cls = cast(PeeweeModelWithMeta, cls)

        db_proxy = meta_cls._meta.database
        if isinstance(db_proxy, peewee.DatabaseProxy):
            db = cast(peewee.Database, db_proxy.obj)
        else:
            db = cast(peewee.Database, db_proxy)

        if isinstance(db, peewee.PostgresqlDatabase):
            cls.insert_many(data).on_conflict(
                'update', conflict_target=[cls.trigger_type_id], update={cls.status: True}
            ).execute()
        else:
            cls.insert_many(data).on_conflict_replace().execute()


class TriggerStatusDoesNotExist(Exception):
    """An exception raised when trying to access a not existing table."""


class OrphanFile(StandardTable):
    """A Model for the files to be removed from disc"""

    file_id = AutoField(primary_key=True, help_text='Primary key')
    filenames = FileNameListField(help_text='The path to the file to be deleted', checksum_field='checksum')
    checksum = FileChecksumField(help_text='The checksum of the files in the list.')


class OrphanFileDoesNotExist(peewee.DoesNotExist):
    """An exception raised when trying to access a not existing table."""


class PlotterOutput(StandardTable):
    """
    A model for the output of the plotter processors.

    The model has a trigger activated on delete queries to insert filenames and checksum in the OrphanFile model.
    """

    plotter_name = CharField(primary_key=True, help_text='The plotter processor name', max_length=511)
    filename_list = FileNameListField(help_text='The path to the output file', checksum_field='checksum')
    checksum = FileChecksumField(help_text='The checksum of the files in the list.')

    @classmethod
    def triggers(cls) -> list[Trigger]:
        insert_into_orphan = Trigger('plotter_delete_file', (TriggerWhen.Before, TriggerAction.Delete), cls, safe=True)
        # warning:
        #   we cannot use the filenames for both the filenames and checksum fields because it is a bare sql statement
        insert_into_orphan.add_sql(
            'INSERT INTO orphan_file (filenames, checksum) VALUES (OLD.filename_list, OLD.checksum);'
        )
        return [insert_into_orphan]

    class Meta:
        depends_on = [OrphanFile]


class PlotterOutputDoesNotExist(peewee.DoesNotExist):
    """An exception raised when trying to access a not existing table."""


standard_tables: dict[str, type[StandardTable]] = {}
"""
A dictionary containing the standard tables being exported to the rest of the framework. 

The key is the name of the model and the value is the model class itself.
"""

standard_tables.update({'TriggerStatus': TriggerStatus, 'OrphanFile': OrphanFile, 'PlotterOutput': PlotterOutput})
