import os
import random
from pathlib import Path
from typing import Any, Iterable

import pytest
from peewee import AutoField, BooleanField, Database, FloatField, ForeignKeyField, SqliteDatabase, TextField
from tomlkit import document, table
from tomlkit.toml_file import TOMLFile

from mafw.db.db_configurations import default_conf
from mafw.db.db_filter import Filter, FilterRegister
from mafw.db.db_model import MAFwBaseModel, database_proxy
from mafw.db.fields import FileChecksumField, FileNameField
from mafw.decorators import single_loop
from mafw.enumerators import LoopType
from mafw.processor import ActiveParameter, Processor


@pytest.fixture
def basic_conf() -> dict:
    doc = document()

    # prepare and add the generic filter table
    tbl = table()
    tbl['new_only'] = True
    tbl['field1'] = 31
    tbl['field3'] = 'something'
    doc.add('GlobalFilter', tbl)

    # prepare and add the processor/model specific filter table
    # first the model table
    mdl_tbl = table()
    mdl_tbl['field1'] = 32
    mdl_tbl['field2'] = 15

    flt_tbl = table()
    flt_tbl.add('MyModel', mdl_tbl)

    proc_tbl = table()
    proc_tbl.add('param1', 12)
    proc_tbl.add('Filter', flt_tbl)

    doc.add('MyProcessor', proc_tbl)

    return doc.value


def test_basic():
    class MeasModel(MAFwBaseModel):
        meas_id = AutoField(primary_key=True)
        sample_name = TextField()
        successful = BooleanField()

    flt = Filter('MyProcessor.Filter.MyModel', sample_name='sample_00*', meas_id=[1, 2, 3], successful=True)
    flt.bind(MeasModel)
    flt.filter()


# noinspection PyUnresolvedReferences
def test_build_filter_from_conf(basic_conf):
    # testing creation of a specific filter overruling generic options and existing
    flt = Filter.from_conf('MyProcessor.Filter.MyModel', basic_conf, default=basic_conf['GlobalFilter'])
    assert flt.field1 == 32
    assert flt.field2 == 15
    assert flt.field3 == 'something'

    # testing creation of a specific filter not existing in the configuration file
    try:
        flt = Filter.from_conf('MyProcessor.Filter.MySecondModel', basic_conf)
    except Exception as e:
        pytest.fail('No error message expected %s', str(e.value))


# noinspection PyUnresolvedReferences
def test_build_filter_from_toml(datadir):
    doc = TOMLFile(datadir / 'basic_conf.toml').read()

    flt = Filter.from_conf('MyProcessor.Filter.MyModel', doc.value)
    assert flt.field1 == 101
    assert flt.field2 == 'ciccia'

    flt = Filter.from_conf('MyProcessor.Filter.MyOtherModel', doc.value)
    assert flt.field1 == -1
    assert flt.field2 == 1

    flt = Filter.from_conf('AnotherProcessor.Filter.MyModel', doc.value)
    assert flt.field1 == 1


def test_processor_and_filter_loading(basic_conf, datadir):
    @single_loop
    class MyProcessor(Processor):
        param1 = ActiveParameter('param1', 144, help_doc='A useless parameter')

    my_proc = MyProcessor(config=basic_conf)
    flt = my_proc.get_filter('MyModel')
    assert my_proc.filter_register.new_only
    assert flt.field1 == 32
    assert flt.field2 == 15

    doc = TOMLFile(datadir / 'basic_conf.toml').read()
    my_proc = MyProcessor(config=doc.value)
    assert len(my_proc.filter_register) == 2
    assert set(list(my_proc.filter_register.keys())) == {'MyModel', 'MyOtherModel'}

    flt = my_proc.get_filter('MyModel')
    assert flt.field2 == 'ciccia'
    assert flt.field1 == 101
    assert flt.field_list == [1, 2, 3]

    flt = my_proc.get_filter('MyOtherModel')
    assert flt.field2 == 1
    assert flt.field1 == -1
    assert not flt.is_bound

    class MyModel(MAFwBaseModel):
        id_ = AutoField(primary_key=True)

    @single_loop
    class AnotherProcessor(Processor):
        pass

    another_proc = AnotherProcessor(config=doc.value)
    assert len(another_proc.filter_register) == 2
    assert set(list(another_proc.filter_register.keys())) == {'MyModel', 'MyOtherModel'}

    flt = another_proc.get_filter('MyModel')
    assert flt.field1 == 1
    assert not flt.is_bound
    flt.bind(MyModel)
    assert flt.is_bound


def test_filter_functionality(datadir):
    doc = TOMLFile(datadir / 'basic_conf.toml').read()

    class AnotherProcessor(Processor):
        pass

    another_proc = AnotherProcessor(config=doc.value, looper=LoopType.SingleLoop)
    for name in another_proc.filter_register:
        # field3 belong only to the GlobalFilter, but all other filter should have
        assert not another_proc.filter_register[name].field3

    class MyModel(MAFwBaseModel):
        id_ = AutoField(primary_key=True)
        sample_name = TextField()

    class MyOtherModel(MAFwBaseModel):
        id_ = AutoField(primary_key=True)
        sample_name = TextField()

    flt1 = another_proc.get_filter('MyModel')
    flt1.bind(MyModel)

    flt2 = another_proc.get_filter('MyOtherModel')
    flt2.bind(MyOtherModel)

    database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)
    database.create_tables([MyModel, MyOtherModel], safe=True)
    MyModel.delete().execute()

    data = []
    n = 100
    for i in range(n):
        data.append(dict(sample_name=f'Sample_{i:05}'))
    MyModel.insert_many(data).execute()
    MyOtherModel.insert_many(data).execute()

    assert MyModel.select().count() == n
    assert MyOtherModel.select().count() == n

    filtered = MyModel.select().where(flt1.filter())
    assert filtered.count() == 10

    filtered = MyOtherModel.select().where(flt2.filter())
    assert filtered.count() == len(flt2.id_)
    for f in filtered:
        assert f.id_ in flt2.id_


def test_filter_type_discrimination(datadir):
    doc = TOMLFile(datadir / 'basic_conf.toml').read()

    class MyProcessor(Processor):
        pass

    my_pc = MyProcessor(config=doc.value, looper='single')

    class MyModel(MAFwBaseModel):
        id_ = AutoField(primary_key=True)
        sample_name = TextField()

    flt = my_pc.get_filter('MyModel')
    flt.bind(MyModel)

    assert isinstance(flt.field1, int)
    assert isinstance(flt.field2, str)
    assert isinstance(flt.field_list, list)


@pytest.fixture
def advanced_models() -> tuple:
    class Sample(MAFwBaseModel):
        sample_id = AutoField(primary_key=True, help_text='The sample id primary key')
        sample_name = TextField(help_text='The sample name')

    class Resolution(MAFwBaseModel):
        resolution_id = AutoField(primary_key=True, help_text='The resolution id primary key')
        resolution_value = FloatField(help_text='The resolution in µm')

    class Image(MAFwBaseModel):
        image_id = AutoField(primary_key=True, help_text='The image id primary key')
        filename = FileNameField(help_text='The filename of the image', checksum_field='checksum')
        checksum = FileChecksumField(help_text='The checksum of the input file')
        sample = ForeignKeyField(
            Sample, Sample.sample_id, on_delete='CASCADE', backref='sample', column_name='sample_id'
        )
        resolution = ForeignKeyField(
            Resolution, Resolution.resolution_id, on_delete='CASCADE', backref='resolution', column_name='resolution_id'
        )

    class ProcessedImage(MAFwBaseModel):
        image = ForeignKeyField(
            Image,
            Image.image_id,
            primary_key=True,
            column_name='image_id',
            backref='raw',
            help_text='The image id, foreign key and primary',
            on_delete='CASCADE',
        )
        value = FloatField(default=0)

    return Sample, Resolution, Image, ProcessedImage


def generate_files(path: Path, n_total: int):
    output_files = []
    for i_file in range(1, n_total + 1):
        filename = path / Path(f'file_{i_file:03}.dat')
        filesize = random.randint(1024, 2048)
        with open(filename, 'wb') as fout:
            fout.write(os.urandom(filesize))
        output_files.append(filename)
    return output_files


def test_full_filter_functionality(shared_datadir, advanced_models, datadir):
    db_file = shared_datadir / 'advanced_db.db'
    database: Database = SqliteDatabase(db_file, pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)

    Sample, Resolution, Image, ProcessedImage = advanced_models
    database.create_tables([Sample, Resolution, Image, ProcessedImage])

    class AdvProcessor(Processor):
        def get_items(self) -> Iterable[Any]:
            """Gets the input lists from a double join and filtering"""
            self.filter_register.bind_all([Sample, Resolution, Image])

            existing_entries = ProcessedImage.select(ProcessedImage.image_id).execute()
            if self.filter_register.new_only:
                existing = ~Image.image_id.in_([i.image_id for i in existing_entries])
            else:
                existing = True

            query = (
                Image.select(Image, Sample, Resolution)
                .join(Sample, on=(Image.sample_id == Sample.sample_id), attr='s')
                .switch(Image)
                .join(Resolution, on=(Image.resolution_id == Resolution.resolution_id), attr='r')
                .where(self.filter_register.filter_all())
                .where(existing)
            )
            return query

        def process(self):
            """Put in the output table only the even images"""
            if self.item.image_id % 2 == 0:
                new_image, _ = ProcessedImage().get_or_create(image_id=self.item.image_id)
                new_image.value = random.randint(0, 100) / random.randint(1, 100)
                new_image.save()

    toml_conf = TOMLFile(datadir / 'adv_db.toml').read().value
    adv_processor = AdvProcessor(database=database, config=toml_conf)
    adv_processor.execute()
    # we expect to have no execution because all output items are already there.
    assert toml_conf['GlobalFilter']['new_only']
    assert adv_processor.n_item == 0
    # check that all filters have the 'just_noise' field
    for flt_name in adv_processor.filter_register:
        assert adv_processor.filter_register[flt_name].just_noise == 'something useless'

    # change conf
    toml_conf['GlobalFilter']['new_only'] = False
    adv_processor = AdvProcessor(database=database, config=toml_conf)
    adv_processor.execute()
    assert adv_processor.n_item == 1
    assert adv_processor.item.image_id == 40

    database.close()


def test_register(datadir, basic_conf):
    # assert default assignment of new_only
    register = FilterRegister()
    assert register.new_only
