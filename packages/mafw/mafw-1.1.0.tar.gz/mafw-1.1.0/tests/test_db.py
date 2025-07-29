"""
Module tests the basic functionality of the database interface.

.. note::

    For the time being, the test is limited to the Sqlite interface, since have no way to test the other
    concrete implementations.
"""

import datetime
import os
import pathlib
import random
from pathlib import Path

import peewee
import pytest
from peewee import (
    SQL,
    AutoField,
    CharField,
    Database,
    DateField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    SqliteDatabase,
    TextField,
    fn,
)

# noinspection PyUnresolvedReferences
from playhouse.db_url import connect

# noinspection PyUnresolvedReferences
from playhouse.signals import post_save
from pwiz import make_introspector

import mafw
from mafw.db.db_configurations import default_conf
from mafw.db.db_model import MAFwBaseModel, database_proxy
from mafw.db.db_wizard import dump_models
from mafw.db.fields import FileChecksumField, FileNameField, FileNameListField
from mafw.db.std_tables import OrphanFile
from mafw.db.trigger import Trigger, TriggerAction, TriggerWhen, and_, or_
from mafw.decorators import database_required, orphan_protector, single_loop
from mafw.enumerators import LoopType, ProcessorExitStatus
from mafw.processor import ActiveParameter, Processor, ProcessorList
from mafw.tools.file_tools import file_checksum, remove_widow_db_rows, verify_checksum


class Person(MAFwBaseModel):
    person_id = AutoField()
    name = CharField()
    birthday = DateField()


class Pet(MAFwBaseModel):
    pet_id = AutoField()
    owner = ForeignKeyField(Person, backref='pets')
    name = CharField()
    animal_type = CharField()


@pytest.fixture
def default_sqlite_pragmas():
    return {'journal_mode': 'wal', 'cache_size': -32000, 'foreign_keys': 1, 'synchronous': 0}


@pytest.fixture
def simple_model() -> list[type[MAFwBaseModel]]:
    return [Person, Pet]


@pytest.fixture
def person_data() -> list[dict]:
    return [
        {'name': 'Toto', 'birthday': datetime.date.fromisoformat('2011-02-15')},
        {'name': 'Tata', 'birthday': datetime.date.fromisoformat('2011-02-15')},
        {'name': 'Giu', 'birthday': datetime.date.fromisoformat('2011-02-15')},
        {'name': 'Jack', 'birthday': datetime.date.fromisoformat('2008-11-22')},
        {'name': 'Teddy', 'birthday': datetime.date.fromisoformat('2014-02-01')},
    ]


@pytest.fixture
def pet_data() -> list[dict]:
    return [
        {'name': 'Topo', 'owner': 1, 'animal_type': 'Cat'},
        {'name': 'Kingo', 'owner': 1, 'animal_type': 'Dog'},
        {'name': 'Goldy', 'owner': 4, 'animal_type': 'Gold fish'},
    ]


def test_db_basics(default_sqlite_pragmas: dict, simple_model: list[type[MAFwBaseModel]]):
    database = SqliteDatabase(':memory:', pragmas=default_sqlite_pragmas)
    database_proxy.initialize(database)

    # check that the database has no tables
    # noinspection PyTypeChecker
    assert len(database.get_tables()) == 0

    # create the tables
    database.create_tables(simple_model)

    # check that the database has the right number of tables.
    # noinspection PyTypeChecker
    assert len(database.get_tables()) == len(simple_model)

    # check that the names of the tables are matching the expectation
    # noinspection PyNoneFunctionAssignment
    db_names = database.get_tables()
    # noinspection PyUnresolvedReferences
    model_names = [model._meta.name for model in simple_model]
    # noinspection PyTypeChecker
    assert sorted(db_names) == sorted(model_names)

    # create an entry but insert it in the DB only with the save
    toto = Person(name='toto', birthday=datetime.date.fromisoformat('1976-03-23'))
    # check that toto did not yet get an id
    assert toto.person_id is None
    toto.save()
    # now it has an id
    assert toto.person_id == 1

    # create an entry and insert it directly to the DB.
    tata = Person.create(name='tata', birthday=datetime.date.fromisoformat('1984-03-24'))
    assert tata.person_id == 2

    family = [
        {'name': 'Jack', 'birthday': datetime.date.fromisoformat('2008-11-22')},
        {'name': 'Giu', 'birthday': datetime.date.fromisoformat('2011-02-15')},
    ]
    Person.insert_many(family).execute()

    family_members = Person.select()
    assert len(family_members) == 4
    assert Person.select().count() == 4

    # get a single person
    jack = Person.get(Person.name == 'Jack')

    # add some pets
    topo = Pet.create(owner=toto, name='topo', animal_type='Cat')
    Pet.create(owner=toto, name='kingo', animal_type='Dog')
    Pet.create(owner=jack, name='goldy', animal_type='Gold fish')
    assert Pet.select().count() == 3

    # check the backref
    # noinspection PyUnresolvedReferences
    assert toto.pets.count() == 2

    # do a selection on backref
    # noinspection PyUnresolvedReferences
    assert toto.pets.select(Pet.name).where(Pet.animal_type == 'Cat').get().name == topo.name


def test_db_creation_file(datadir, default_sqlite_pragmas, simple_model, person_data, pet_data):
    new_db = datadir / Path('empty_db.db')
    new_db.unlink(missing_ok=True)

    database = SqliteDatabase(new_db, pragmas=default_sqlite_pragmas)
    database_proxy.initialize(database)
    database.connect()

    # create the tables
    with database.atomic():
        database.create_tables(simple_model)
        Person.insert_many(person_data).execute()
        Pet.insert_many(pet_data).execute()

    assert Person.select().count() == len(person_data)

    database.close()

    database = SqliteDatabase(new_db, pragmas=default_sqlite_pragmas)
    database_proxy.initialize(database)
    assert Person.select().count() == len(person_data)
    database.close()


def test_db_readback_file(datadir, simple_model, default_sqlite_pragmas, person_data):
    full_db = datadir / 'full_db.db'

    database = SqliteDatabase(full_db, pragmas=default_sqlite_pragmas)
    # verify that the pragmas have been correctly assigned
    for key, value in default_sqlite_pragmas.items():
        assert getattr(database, key) == value

    database_proxy.initialize(database)
    database.connect(reuse_if_open=True)

    with pytest.raises(peewee.OperationalError) as e:
        database.connect(reuse_if_open=False)
    assert 'Connection already opened' in str(e.value)

    assert Person.select().count() == len(person_data)
    got_names = [p.name for p in Person.select()]
    set_names = [p['name'] for p in person_data]
    assert sorted(got_names) == sorted(set_names)


def test_db_readback_with_connect(datadir, simple_model, default_sqlite_pragmas, person_data):
    full_db = datadir / 'full_db.db'
    url = f'sqlite:///{str(full_db)}'

    database = connect(url, pragmas=default_sqlite_pragmas)
    database_proxy.initialize(database)
    database.connect()

    # verify that the pragmas have been correctly assigned
    for key, value in default_sqlite_pragmas.items():
        assert getattr(database, key) == value

    assert Person.select().count() == len(person_data)
    got_names = [p.name for p in Person.select()]
    set_names = [p['name'] for p in person_data]
    assert sorted(got_names) == sorted(set_names)


def test_db_failure_connect():
    url = 'sqlite:/*/:memory:'
    database = connect(url)
    with pytest.raises(peewee.OperationalError):
        database.connect()


def test_and_or_conditions():
    a = and_('a == b', 'c == d')
    b = or_('a == b', 'c == d')
    c = and_(a, b)
    d = or_('a==0')
    assert a == '(a == b) AND (c == d)'
    assert b == '(a == b) OR (c == d)'
    assert c == '((a == b) AND (c == d)) AND ((a == b) OR (c == d))'
    assert d == '(a==0)'


def test_signals():
    class MyTable(MAFwBaseModel):
        id_ = AutoField(primary_key=True)
        integer = IntegerField()
        float_num = FloatField()

    class TargetTable(MAFwBaseModel):
        id_ = ForeignKeyField(MyTable, on_delete='cascade', primary_key=True, backref='half')
        another_float_num = FloatField()

    @post_save(sender=MyTable, name='my_table_after_save_handler')
    def post_save_of_my_table(sender: type(MAFwBaseModel), instance: MAFwBaseModel, created: bool):
        """
        Handler for the post save signal.

        The post_save decorator is taking care of making the connection.
        The sender specified in the decorator argument is assuring that only signals generated from MyClass will be
        dispatched to this handler.

        The name in the decorator is optional and can be use if we want to disconnect the signal from the handler.

        :param sender: The Model class sending this signal.
        :type sender: type(Model)
        :param instance: The actual instance sending the signal.
        :type instance: Model
        :param created: Bool flag if the instance has been created.
        :type created: bool
        """
        TargetTable.insert({'id__id': instance.id, 'another_float_num': instance.float_num / 2}).execute()

    database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)
    database.create_tables([MyTable, TargetTable], safe=True)

    MyTable.delete().execute()
    TargetTable.delete().execute()

    # insert a single row in MyTable with the save method.
    my_table = MyTable()
    my_table.integer = 20
    my_table.float_num = 32.16
    my_table.save()
    # after the save query is done, the signal mechanism will call the
    # post_save_trigger_of_my_table and perform an insert on the target
    # table as well.
    assert MyTable.select().count() == 1
    assert TargetTable.select().count() == 1

    # add some bulk data to MyTable
    data = []
    for i in range(100):
        data.append(dict(integer=random.randint(i, 10 * i), float_num=random.gauss(i, 2 * i)))
    MyTable.insert_many(data).execute()
    # this is done via the Model class and not via a concrete instance of the Model, so no signals will be emitted.

    assert MyTable.select().count() == 101
    assert TargetTable.select().count() == 1


def generate_files(path: pathlib.Path, n_total: int):
    file_list = []
    for i_file in range(1, n_total + 1):
        filename = path / Path(f'file_{i_file:03}.dat')
        filesize = random.randint(1024, 2048)
        file_list.append(filename)
        with open(filename, 'wb') as fout:
            fout.write(os.urandom(filesize))
    return file_list


def remove_some_files(path: pathlib.Path, index_list: list[int]):
    for i_file in index_list:
        filename = path / Path(f'file_{i_file:03}.dat')
        filename.unlink(missing_ok=True)


def change_some_files(path: pathlib.Path, index_list: list[int]):
    for i_file in index_list:
        filename = path / Path(f'file_{i_file:03}.dat')
        with open(filename, 'rb') as fd:
            inp = fd.read()
        with open(filename, 'wb') as fd:
            fd.write(inp[1:])


def test_file_field(tmp_path):
    class MyData(MAFwBaseModel):
        data_id = AutoField(primary_key=True, help_text='The primary key')
        file_name = FileNameField(help_text='The full filename', checksum_field='file_digest')
        file_digest = FileChecksumField(help_text='The hex digest of the file')

    database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)
    database.create_tables([MyData], safe=True)
    MyData.delete().execute()

    n_total = 100
    generate_files(tmp_path, n_total)

    data = []
    for file in sorted(tmp_path.glob('*dat')):
        data.append(dict(file_name=file, file_digest=file_checksum(file)))

    MyData.insert_many(data).execute()

    data_id = [f.data_id for f in MyData.select()]
    assert len(data_id) == n_total

    n_removed = 15
    removed_id = random.sample(data_id, n_removed)
    remove_some_files(tmp_path, removed_id)

    remove_widow_db_rows(MyData)

    remaining_id = [f.data_id for f in MyData.select()]
    assert len(remaining_id) == n_total - n_removed
    assert set(remaining_id) == set(data_id) - set(removed_id)

    n_modified = 15
    modified_id = random.sample(remaining_id, n_modified)
    change_some_files(tmp_path, modified_id)

    verify_checksum(MyData)

    remaining_id2 = [f.data_id for f in MyData.select()]
    assert len(remaining_id2) == n_total - n_removed - n_modified
    assert set(remaining_id2) == set(remaining_id) - set(modified_id)


def verify_checksum_and_widow_on_list(tmp_path):
    class MyData(MAFwBaseModel):
        data_id = AutoField(primary_key=True, help_text='The primary key')
        file_name_list = FileNameField(help_text='A list filename', checksum_field='file_digest')
        file_digest = FileChecksumField(help_text='The hex digest of the file')

    database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)
    database.create_tables([MyData], safe=True)
    MyData.delete().execute()

    n_total = 10
    file_list = generate_files(tmp_path, n_total)

    my_data = MyData()
    my_data.file_name_list = file_list
    my_data.save()

    assert MyData.select().count() == 1
    retrieved_data = MyData.get_by_id(my_data.data_id)
    assert len(retrieved_data.file_name_list) == n_total
    assert retrieved_data.file.digest == mafw.tools.file_tools.file_checksum(file_list)

    # attempt to remove widow rows
    remove_widow_db_rows(MyData)

    # since all files are still present, the row will be preserved.
    assert MyData.select().count() == 1

    # remove one file
    file_list[0].unlink()

    # remove widows rows
    remove_widow_db_rows(MyData)

    # since one file is missing, the whole row must be deleted.
    assert MyData.select().count() == 0

    # do it again
    n_total = 10
    file_list = generate_files(tmp_path, n_total)

    my_data = MyData()
    my_data.file_name_list = file_list
    my_data.save()

    assert MyData.select().count() == 1
    retrieved_data = MyData.get_by_id(my_data.data_id)
    assert len(retrieved_data.file_name_list) == n_total
    assert retrieved_data.file.digest == mafw.tools.file_tools.file_checksum(file_list)

    # verify the checksum
    verify_checksum(MyData)
    # everything is as it should, so the row is preserved
    assert MyData.select().count() == 1

    # now modify one file
    change_some_files(tmp_path, [random.choice(range(n_total))])

    # verify the checksum
    verify_checksum(MyData)

    # since one file is different, the whole row must be deleted.
    assert MyData.select().count() == 0


def test_filename_list_field(tmp_path):
    class MyData(MAFwBaseModel):
        data_id = AutoField(primary_key=True, help_text='The primary key')
        file_name_list = FileNameListField(help_text='A list of filenames', checksum_field='file_list_digest')
        file_list_digest = FileChecksumField(help_text='The hex digest of the file')

    database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)
    database.create_tables([MyData], safe=True)
    MyData.delete().execute()

    n_total = 10
    file_list = generate_files(tmp_path, n_total=n_total)

    # set only the file_name_list, let the checksum be auto-initialised
    my_data = MyData()
    my_data.file_name_list = file_list
    my_data.save()

    retrieved_data = MyData.get_by_id(my_data.data_id)
    assert retrieved_data.file_list_digest == mafw.tools.file_tools.file_checksum(file_list)

    file_list = generate_files(tmp_path, n_total=n_total)

    # set both file_name_list and checksum
    my_data = MyData()
    my_data.file_name_list = file_list
    my_data.file_list_digest = file_list
    my_data.save()

    retrieved_data = MyData.get_by_id(my_data.data_id)
    assert retrieved_data.file_list_digest == mafw.tools.file_tools.file_checksum(file_list)

    file_list = generate_files(tmp_path, n_total=n_total)

    # set both file_name_list and checksum
    # but now in the opposite order
    my_data = MyData()
    my_data.file_list_digest = file_list
    my_data.file_name_list = file_list
    my_data.save()

    retrieved_data = MyData.get_by_id(my_data.data_id)
    assert retrieved_data.file_list_digest == mafw.tools.file_tools.file_checksum(file_list)

    file_list = generate_files(tmp_path, n_total=n_total)

    # set both file_name_list and checksum
    # but now with the real checksum and not the list
    my_data = MyData()
    my_data.file_list_digest = file_list
    my_data.file_name_list = mafw.tools.file_tools.file_checksum(file_list)
    my_data.save()

    retrieved_data = MyData.get_by_id(my_data.data_id)
    assert retrieved_data.file_list_digest == mafw.tools.file_tools.file_checksum(file_list)

    # set both file_name_list and checksum
    # but before the save, remove one file.
    # this will throw an exception
    my_data = MyData()
    my_data.file_list_digest = file_list
    my_data.file_name_list = file_list

    file_list[0].unlink()

    with pytest.raises(FileNotFoundError):
        my_data.save()

    file_list = generate_files(tmp_path, n_total=1)

    # set the filename with only 1 file, not a list
    my_data = MyData()
    my_data.file_name_list = file_list[0]
    my_data.save()

    retrieved_data = MyData.get_by_id(my_data.data_id)
    assert retrieved_data.file_list_digest == mafw.tools.file_tools.file_checksum(file_list)
    assert retrieved_data.file_list_digest == mafw.tools.file_tools.file_checksum(file_list[0])
    assert len(retrieved_data.file_name_list) == 1


def test_checksum_field_with_wrong_filename(tmp_path):
    class MyData(MAFwBaseModel):
        data_id = AutoField(primary_key=True, help_text='The primary key')
        file_name = FileNameField(help_text='The full filename', checksum_field='WRONG_file_digest')
        file_digest = FileChecksumField(help_text='The hex digest of the file')

    database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)
    database.create_tables([MyData], safe=True)
    MyData.delete().execute()

    generate_files(tmp_path, 1)
    data = []
    for file in tmp_path.glob('*dat'):
        data.append(dict(file_name=file, file_digest=file_checksum(file)))

    MyData.insert_many(data).execute()

    with pytest.raises(mafw.mafw_errors.ModelError, match='WRONG_file_digest'):
        verify_checksum(MyData)


def test_checksum_field_with_missing_file(tmp_path):
    class MyData(MAFwBaseModel):
        data_id = AutoField(primary_key=True, help_text='The primary key')
        file_name = FileNameField(help_text='The full filename', checksum_field='file_digest')
        file_digest = FileChecksumField(help_text='The hex digest of the file')

    database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)
    database.create_tables([MyData], safe=True)
    MyData.delete().execute()

    generate_files(tmp_path, 1)
    data = []
    for file in tmp_path.glob('*dat'):
        data.append(dict(file_name=file, file_digest=file_checksum(file)))

    MyData.insert_many(data).execute()

    remove_some_files(tmp_path, [1])

    with pytest.warns(UserWarning, match='file_001.dat'):
        verify_checksum(MyData)

    assert MyData.select().count() == 0


def test_checksum_field_automatic_generation(tmp_path):
    class MyData(MAFwBaseModel):
        data_id = AutoField(primary_key=True, help_text='The primary key')
        file_name = FileNameField(help_text='The full filename')
        file_digest = FileChecksumField(help_text='The hex digest of the file')

    database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)
    database.create_tables([MyData], safe=True)
    MyData.delete().execute()

    generate_files(tmp_path, 4)
    file = tmp_path / 'file_001.dat'
    data = MyData()
    data.file_name = file
    data.file_digest = file  # assigned file (Path) and not the digest
    data.save()
    data_id = data.data_id

    digest = file_checksum(file)
    saved_data = MyData.get_by_id(data_id)
    assert digest == saved_data.file_digest

    file = tmp_path / 'file_002.dat'
    data = MyData()
    data.file_name = file
    data.file_digest = str(file)  # assigned file (str) and not the digest
    data.save()
    data_id = data.data_id

    digest = file_checksum(file)
    saved_data = MyData.get_by_id(data_id)
    assert digest == saved_data.file_digest

    file = tmp_path / 'file_003.dat'
    data = MyData()
    data.file_name = file
    data.file_digest = mafw.tools.file_tools.file_checksum(file)  # assigned checksum
    data.save()
    data_id = data.data_id

    digest = file_checksum(file)
    saved_data = MyData.get_by_id(data_id)
    assert digest == saved_data.file_digest


def test_filechecksum_accessor(tmp_path):
    # testing unbound field
    field = FileChecksumField()
    assert isinstance(field, FileChecksumField)

    class MyData(MAFwBaseModel):
        data_id = AutoField(primary_key=True, help_text='The primary key')
        file_name = FileNameField(help_text='The full filename', checksum_field='file_digest')
        file_digest = FileChecksumField(help_text='The hex digest of the file')

    database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)
    database.create_tables([MyData], safe=True)
    MyData.delete().execute()

    # testing bound field as class attribute
    assert isinstance(MyData.file_digest, FileChecksumField)

    my_data = MyData(file_name=Path.cwd(), file_digest='pino')
    assert my_data.file_digest == 'pino'

    my_data = MyData(file_name=Path.cwd())
    assert my_data.file_digest == my_data.file_name

    my_data = MyData()
    my_data.file_name = Path.cwd()
    assert my_data.file_digest == my_data.file_name

    my_data = MyData()
    my_data.file_name = Path.cwd()
    my_data.file_digest = '123'
    assert my_data.file_digest == '123'
    # #
    generate_files(tmp_path, 4)
    file = tmp_path / 'file_001.dat'
    data = MyData()
    data.file_name = file
    data.file_digest = file  # assigned file (Path) and not the digest
    data.save()
    data_id = data.data_id
    #
    digest = file_checksum(file)
    saved_data = MyData.get_by_id(data_id)
    assert digest == saved_data.file_digest

    file = tmp_path / 'file_002.dat'
    data = MyData()
    data.file_name = file
    data.save()
    data_id = data.data_id

    digest = file_checksum(file)
    saved_data = MyData.get_by_id(data_id)
    assert digest == saved_data.file_digest

    file = tmp_path / 'file_003.dat'
    data = MyData()
    data.file_name = file
    data.file_digest = 'pippo'
    data.init_file_digest = False
    data.file_name = file
    data.save()
    data_id = data.data_id

    digest = file_checksum(file)
    saved_data = MyData.get_by_id(data_id)
    assert digest == saved_data.file_digest


def test_upsert():
    class TriggerEvent(MAFwBaseModel):
        event_id = AutoField(primary_key=True, help_text='The primary key')
        source_table = TextField(help_text='The table generating the trigger')
        source_pk = TextField(help_text='The primary key of the source table row causing the trigger')
        trigger_name = TextField(help_text='The name of the trigger')
        trigger_action = TextField(help_text='The trigger action')
        trigger_when = TextField(help_text='The trigger when')

    class Sample(MAFwBaseModel):
        sample_id = AutoField(primary_key=True, help_text='The sample id primary key')
        sample_name = TextField(help_text='The sample name')

        @classmethod
        def triggers(cls) -> list[Trigger]:
            insert_trg = Trigger(
                'sample_insert',
                (TriggerWhen.After, TriggerAction.Insert),
                source_table='sample',
                safe=True,
                for_each_row=True,
            )

            sql = TriggerEvent.insert(
                source_table=insert_trg.target_table,
                source_pk=SQL('NEW.sample_id'),
                trigger_name=insert_trg.trigger_name,
                trigger_action=str(insert_trg.trigger_action),
                trigger_when=str(insert_trg.trigger_when),
            )
            insert_trg.add_sql(sql)

            update_trg = Trigger(
                'sample_update',
                (TriggerWhen.After, TriggerAction.Update),
                source_table='sample',
                safe=True,
                for_each_row=True,
            )
            sql = TriggerEvent.insert(
                source_table=update_trg.target_table,
                source_pk=SQL('NEW.sample_id'),
                trigger_name=update_trg.trigger_name,
                trigger_action=str(update_trg.trigger_action),
                trigger_when=str(update_trg.trigger_when),
            )
            update_trg.add_sql(sql)
            update_trg.add_when('NEW.sample_name != OLD.sample_name')
            return [insert_trg, update_trg]

        class Meta:
            depends_on = [TriggerEvent]

    database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)
    database.create_tables([Sample, TriggerEvent], safe=True)

    # empty table
    TriggerEvent.delete()
    Sample.delete()

    # upsert samples
    # perfom single upsert in loop
    n_samples = 10
    for i in range(n_samples):
        Sample.std_upsert(sample_id=i, sample_name=f'Sample_{i:03}').execute()

    # assert that query was successful
    assert Sample.select().count() == n_samples

    # assert that we recorded  insert events
    assert TriggerEvent.select().count() == n_samples
    assert TriggerEvent.select().where(TriggerEvent.trigger_name == 'sample_insert').count() == n_samples

    n_change = 3
    rnd_samples = Sample.select().order_by(fn.Random()).limit(n_change)
    for sample in rnd_samples:
        sample.sample_name = 'RND'
        sample.save()

    assert Sample.select().where(Sample.sample_name == 'RND').count() == n_change
    assert TriggerEvent.select().where(TriggerEvent.trigger_name == 'sample_insert').count() == n_samples
    assert TriggerEvent.select().where(TriggerEvent.trigger_name == 'sample_update').count() == n_change

    # repeat upsert
    for i in range(n_samples):
        # this time use a dictionary

        Sample.std_upsert(dict(sample_id=i, sample_name=f'Sample_{i:03}')).execute()

    assert Sample.select().where(Sample.sample_name == 'RND').count() == 0
    assert TriggerEvent.select().where(TriggerEvent.trigger_name == 'sample_insert').count() == n_samples
    assert TriggerEvent.select().where(TriggerEvent.trigger_name == 'sample_update').count() == n_change * 2

    TriggerEvent.delete().execute()
    Sample.delete().execute()
    assert TriggerEvent.select().count() == Sample.select().count()

    # std_upsert_many
    (
        Sample.std_upsert_many(
            [(i, f'Sample_{i:03}') for i in range(n_samples)], fields=[Sample.sample_id, Sample.sample_name]
        ).execute()
    )

    # assert that query was successful
    assert Sample.select().count() == n_samples

    # assert that we recorded  insert events
    assert TriggerEvent.select().count() == n_samples
    assert TriggerEvent.select().where(TriggerEvent.trigger_name == 'sample_insert').count() == n_samples

    n_change = 3
    rnd_samples = Sample.select().order_by(fn.Random()).limit(n_change)
    for sample in rnd_samples:
        sample.sample_name = 'RND'
        sample.save()

    assert Sample.select().where(Sample.sample_name == 'RND').count() == n_change
    assert TriggerEvent.select().where(TriggerEvent.trigger_name == 'sample_insert').count() == n_samples
    assert TriggerEvent.select().where(TriggerEvent.trigger_name == 'sample_update').count() == n_change

    # repeat std_upsert_many
    # this time using a list of dictionary
    (Sample.std_upsert_many([dict(sample_id=i, sample_name=f'Sample_{i:03}') for i in range(n_samples)]).execute())

    assert Sample.select().where(Sample.sample_name == 'RND').count() == 0
    assert TriggerEvent.select().where(TriggerEvent.trigger_name == 'sample_insert').count() == n_samples
    assert TriggerEvent.select().where(TriggerEvent.trigger_name == 'sample_update').count() == n_change * 2

    database.close()


def test_full_orphan(tmp_path):
    class File(MAFwBaseModel):
        file_id = AutoField(primary_key=True, help_text='primary key')
        file_name = FileNameField(checksum_field='check_sum', help_text='the file name')
        check_sum = FileChecksumField(help_text='checksum')

        @classmethod
        def triggers(cls) -> list[Trigger]:
            file_delete_file = Trigger(
                'file_delete_file',
                (TriggerWhen.Before, TriggerAction.Delete),
                source_table=cls,
                safe=True,
                for_each_row=True,
            )
            file_delete_file.add_when('1 == (SELECT status FROM trigger_status WHERE trigger_type = "DELETE_FILES")')
            file_delete_file.add_sql(OrphanFile.insert(filenames=SQL('OLD.file_name'), checksum=SQL('OLD.file_name')))
            return [file_delete_file]

        class Meta:
            depends_on = [OrphanFile]

    # processor definition
    @database_required
    class FileImporter(Processor):
        input_folder = ActiveParameter('input_folder', default=Path.cwd(), help_doc='From where to import')

        def __init__(self, *args, **kwargs):
            super().__init__(*args, looper=LoopType.SingleLoop, **kwargs)
            self.n_files: int = -1

        def start(self):
            super().start()
            self.database.create_tables([File])
            File.delete().execute()

        def process(self):
            data = [(f, f) for f in self.input_folder.glob('**/*dat')]
            File.insert_many(data, fields=['file_name', 'check_sum']).execute()
            self.n_files = len(data)

        def finish(self):
            super().finish()
            if File.select().count() != self.n_files:
                self.processor_exit_status = ProcessorExitStatus.Failed

    @database_required
    class RowRemover(Processor):
        n_rows = ActiveParameter('n_rows', default=0, help_doc='How many rows to be removed')

        def __init__(self, *args, **kwargs):
            super().__init__(*args, looper=LoopType.SingleLoop, **kwargs)
            self.n_initial = 0

        def start(self):
            super().start()
            self.database.create_tables([File])

        def process(self):
            self.n_initial = File.select().count()
            query = File.select().order_by(fn.Random()).limit(self.n_rows).execute()
            ids = [q.file_id for q in query]
            File.delete().where(File.file_id.in_(ids)).execute()

        def finish(self):
            super().finish()
            if File.select().count() != self.n_initial - self.n_rows or OrphanFile.select().count() != self.n_rows:
                self.processor_exit_status = ProcessorExitStatus.Failed

    @orphan_protector
    @database_required
    class OrphanProtector(Processor):
        def __init__(self, *args, **kwargs):
            super().__init__(looper=LoopType.SingleLoop, *args, **kwargs)
            self.n_orphan = 0

        def start(self):
            self.n_orphan = OrphanFile.select().count()
            super().start()

        def finish(self):
            super().finish()
            if OrphanFile.select().count() != self.n_orphan:
                self.processor_exit_status = ProcessorExitStatus.Failed

    @single_loop
    class LazyProcessor(Processor):
        def finish(self):
            super().finish()
            if OrphanFile.select().count() != 0:
                self.processor_exit_status = ProcessorExitStatus.Failed

    # end of processor definition

    n_files = 10
    n_delete = random.randint(1, n_files)
    generate_files(tmp_path, n_files)

    db_conf = default_conf['sqlite']
    db_conf['URL'] = 'sqlite:///:memory:'
    plist = ProcessorList(name='Orphan test', description='dealing with orphan files', database_conf=db_conf)
    importer = FileImporter(input_folder=tmp_path)
    remover = RowRemover(n_rows=n_delete)
    protector = OrphanProtector()
    lazy = LazyProcessor()
    plist.extend([importer, remover, protector, lazy])
    plist.execute()

    assert importer.processor_exit_status == ProcessorExitStatus.Successful
    assert remover.processor_exit_status == ProcessorExitStatus.Successful
    assert protector.processor_exit_status == ProcessorExitStatus.Successful
    assert lazy.processor_exit_status == ProcessorExitStatus.Successful
    assert len(list(tmp_path.glob('**/*dat'))) == n_files - n_delete


def test_db_wizard(tmp_path, shared_datadir):
    output_file = tmp_path / 'my_db.py'
    input_database = shared_datadir / 'advanced_db.db'
    intro = make_introspector('sqlite', input_database)

    with open(output_file, 'w') as out_file:
        dump_models(out_file, intro, preserve_order=True)

    # check that the file exists
    assert output_file.exists()

    # temporary add the module to the path
    import sys

    sys.path.append(str(output_file.parent))

    # import the module. it should not emit any exception
    try:
        import my_db as mydb
    except ImportError:
        pytest.fail('Failed to import the generated model')

    # check that the base class and the image model are in the model
    assert mydb.MAFwBaseModel.__qualname__ in dir(mydb)
    assert mydb.Image.__qualname__ in dir(mydb)

    output_file = tmp_path / 'small_my_db.py'
    tables = ['sample', 'resolution']
    with open(output_file, 'w') as out_file:
        dump_models(out_file, intro, tables=tables, preserve_order=True)

    # check that the file exists
    assert output_file.exists()

    # import the module. it should not emit any exception
    try:
        import small_my_db as small_mydb
    except ImportError:
        pytest.fail('Failed to import the generated model')

    # check that the base class and the image model are in the model
    assert small_mydb.MAFwBaseModel.__qualname__ in dir(small_mydb)
    assert small_mydb.Sample.__qualname__ in dir(small_mydb)
    assert small_mydb.Resolution.__qualname__ in dir(small_mydb)
    with pytest.raises(AttributeError, match="has no attribute 'Image'"):
        assert small_mydb.Image

    output_file = tmp_path / 'view_my_db.py'
    with open(output_file, 'w') as out_file:
        dump_models(out_file, intro, include_views=True)
    # check that the file exists
    assert output_file.exists()

    # import the module. it should not emit any exception
    try:
        import view_my_db as view_mydb
    except ImportError:
        pytest.fail('Failed to import the generated model')
    assert view_mydb.MAFwBaseModel.__qualname__ in dir(view_mydb)
    assert view_mydb.Sample.__qualname__ in dir(view_mydb)
    assert view_mydb.Resolution.__qualname__ in dir(view_mydb)
    assert view_mydb.ImageView.__qualname__ in dir(view_mydb)
