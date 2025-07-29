"""
Module provides tests for the creation of standard tables
"""

import os
import random
from pathlib import Path

from peewee import SqliteDatabase

from mafw.db.db_configurations import default_conf
from mafw.db.db_model import database_proxy
from mafw.db.std_tables import standard_tables
from mafw.decorators import database_required
from mafw.enumerators import LoopType
from mafw.processor import ActiveParameter, Processor, ProcessorList

default_sqlite_pragmas = default_conf['sqlite']['pragmas']


def test_creation_of_std_table():
    database = SqliteDatabase(':memory:', pragmas=default_sqlite_pragmas)
    database_proxy.initialize(database)
    database.create_tables(standard_tables.values())
    for table in standard_tables.values():
        table.init()

    assert len(database.get_tables()) == len(standard_tables)

    TriggerStatus = standard_tables['TriggerStatus']
    assert TriggerStatus.select().count() == 4

    database.close()


def test_creation_of_std_table_via_processor():
    class MyProcessor(Processor):
        n_table = ActiveParameter('n_table', default=-1, help_doc='The number of tables in the database')

        def __init__(self, *args, **kwargs):
            super().__init__(*args, looper=LoopType.SingleLoop, **kwargs)

        def process(self):
            self.n_table = len(self.database.get_tables())

    database = SqliteDatabase(':memory:', pragmas=default_sqlite_pragmas)
    database_proxy.initialize(database)

    # when passing a database object, the tables are not created because the processor thinks to be inside a
    # ProcessorList.
    my_processor = MyProcessor(database=database)
    my_processor.execute()

    assert len(database.get_tables()) == 0
    assert my_processor.n_table == 0

    processor_list = ProcessorList(name='A list of processor', database=database)
    processor_list.append(MyProcessor())
    processor_list.execute()
    assert processor_list[0].n_table == 0

    database.close()

    my_processor = MyProcessor(database_conf=default_conf['sqlite'])
    my_processor.execute()
    assert my_processor.n_table >= 2

    processor_list = ProcessorList(name='A list of processor', database_conf=default_conf['sqlite'])
    processor_list.append(MyProcessor())
    processor_list.execute()
    assert processor_list[0].n_table >= 2


def generate_files(path: Path, n_total: int) -> list[Path]:
    files = []
    for i_file in range(1, n_total + 1):
        filename = path / Path(f'file_{i_file:03}.dat')
        files.append(filename)
        filesize = random.randint(1024, 1025)
        with open(filename, 'wb') as fout:
            fout.write(os.urandom(filesize))
    return files


def test_removing_orphan_files(tmp_path, datadir):
    files = generate_files(tmp_path, 10)
    database_conf = default_conf['sqlite'].copy()
    database_conf['URL'] = 'sqlite:///' + str(datadir / 'empty_db.db')

    @database_required
    class FillInOrphanFileProcessor(Processor):
        orphan_files = ActiveParameter(
            'orphan_files', default=[], help_doc='A list of files to be loaded into the orphan table'
        )
        n_files = ActiveParameter('n_files', default=-1, help_doc='Total number of files in the orphan table')

        def __init__(self, *args, **kwargs):
            super().__init__(*args, looper=LoopType.SingleLoop, **kwargs)

        def process(self):
            OrphanFile = standard_tables.get('OrphanFile')
            self.orphan_files = [dict(filenames=file, checksum=file) for file in self.orphan_files]
            OrphanFile.insert_many(self.orphan_files).execute()
            self.n_files = OrphanFile.select().count()

    @database_required
    class LazyProcessor(Processor):
        initial_n_files = ActiveParameter(
            'initial_n_files', default=-1, help_doc='Total number of files in the orphan table before pruning'
        )
        final_n_files = ActiveParameter(
            'final_n_files', default=-1, help_doc='Total number of files in the orphan table after pruning'
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, looper='single', **kwargs)

        def start(self):
            OrphanFile = standard_tables.get('OrphanFile')
            self.initial_n_files = OrphanFile.select().count()
            super().start()

        def process(self):
            OrphanFile = standard_tables.get('OrphanFile')
            self.final_n_files = OrphanFile.select().count()

    plist = ProcessorList(database_conf=database_conf)

    # this will fill in files to be removed.
    fill_in = FillInOrphanFileProcessor(orphan_files=files)

    # this will count how many files to be removed and then remove them.
    lazy = LazyProcessor()

    plist.append(fill_in)
    plist.append(lazy)

    plist.execute()

    # check that all files were inserted.
    assert fill_in.n_files == len(files)
    # check that all files were still there at the end of the first processor.
    assert lazy.initial_n_files == len(files)
    # check that all files were deleted from the table
    assert lazy.final_n_files == 0
    # check that all files were deleted from the disk
    actual_files = list(tmp_path.glob('*dat'))
    assert len(actual_files) == 0


def test_no_removing_orphan_files(tmp_path, datadir):
    files = generate_files(tmp_path, 10)
    database_conf = default_conf['sqlite'].copy()
    database_conf['URL'] = 'sqlite:///' + str(datadir / 'empty_db.db')

    @database_required
    class FillInOrphanFileProcessor(Processor):
        orphan_files = ActiveParameter(
            'orphan_files', default=[], help_doc='A list of files to be loaded into the orphan table'
        )
        n_files = ActiveParameter('n_files', default=-1, help_doc='Total number of files in the orphan table')

        def __init__(self, *args, **kwargs):
            super().__init__(*args, looper='single', **kwargs)

        def process(self):
            OrphanFile = standard_tables.get('OrphanFile')
            self.orphan_files = [dict(filenames=file, checksum=file) for file in self.orphan_files]
            OrphanFile.insert_many(self.orphan_files).execute()
            self.n_files = OrphanFile.select().count()

    @database_required
    class LazyProcessor(Processor):
        initial_n_files = ActiveParameter(
            'initial_n_files', default=-1, help_doc='Total number of files in the orphan table before pruning'
        )
        final_n_files = ActiveParameter(
            'final_n_files', default=-1, help_doc='Total number of files in the orphan table after pruning'
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, looper='single', **kwargs)

        def start(self):
            OrphanFile = standard_tables.get('OrphanFile')
            self.initial_n_files = OrphanFile.select().count()
            super().start()

        def process(self):
            OrphanFile = standard_tables.get('OrphanFile')
            self.final_n_files = OrphanFile.select().count()

    plist = ProcessorList(database_conf=database_conf)

    # this will fill in files to be removed.
    fill_in = FillInOrphanFileProcessor(orphan_files=files)

    # this will count how many files to be removed and but do not remove them.
    lazy = LazyProcessor(remove_orphan_files=False)

    plist.append(fill_in)
    plist.append(lazy)

    plist.execute()

    # check that all files were inserted.
    assert fill_in.n_files == len(files)
    # check that all files were still there at the end of the first processor.
    assert lazy.initial_n_files == len(files)
    # check that all files were still there in the table
    assert lazy.final_n_files == len(files)
    # check that all files were still there on the disk
    actual_files = list(tmp_path.glob('*dat'))
    assert len(actual_files) == len(files)
