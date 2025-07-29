import itertools
from pathlib import Path

import pytest
from click.testing import CliRunner
from tomlkit.toml_file import TOMLFile

from mafw import mafw_hookimpl
from mafw.decorators import single_loop
from mafw.mafw_errors import MissingOverloadedMethod, MissingSuperCall
from mafw.plugin_manager import get_plugin_manager
from mafw.processor import Processor
from mafw.scripts import mafw_exe
from mafw.tools.file_tools import file_checksum


def test_running_mafw_without_commands():
    runner = CliRunner()
    result = runner.invoke(mafw_exe.cli)
    assert result.output.strip('\n') == 'Use --help to get a quick help on the mafw command.'


def test_help_options():
    runner = CliRunner()
    result = runner.invoke(mafw_exe.cli, ['-h'])
    assert 'Usage: mafw [OPTIONS] COMMAND [ARGS]...' in result.output


def test_list_command():
    runner = CliRunner()
    result = runner.invoke(mafw_exe.cli, ['list'])
    assert 'Available processors (External Plugins = True)' in result.output

    runner = CliRunner()
    result = runner.invoke(mafw_exe.cli, ['list', '--no-ext-plugin'])
    assert 'Available processors (External Plugins = False)' in result.output


def test_steering_command(tmp_path):
    runner = CliRunner()
    result = runner.invoke(mafw_exe.cli, ['steering'])
    assert "Error: Missing argument 'STEERING_FILE'." in result.output

    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        filename = 'test.toml'
        result = runner.invoke(mafw_exe.cli, ['steering', filename])
        assert 'A generic steering file has been saved in test.toml.' in result.output
        output_file = Path(Path(td) / Path(filename))
        assert output_file.exists()
        output_file.unlink(missing_ok=True)

        result = runner.invoke(mafw_exe.cli, ['steering', filename, '--show'])
        assert '# MAFw steering file generated ' in result.output
        assert 'A generic steering file has been saved in test.toml.' in result.output
        output_file = Path(Path(td) / Path(filename))
        assert output_file.exists()

        result = runner.invoke(mafw_exe.cli, ['steering', '--db-engine', 'unknown'])
        assert "Error: Invalid value for '--db-engine': " in result.output

        result = runner.invoke(mafw_exe.cli, ['steering', '--db-engine', 'mysql', filename])
        output_file = Path(Path(td) / Path(filename))
        assert output_file.exists()
        with open(output_file) as fp:
            content = fp.read()
        assert 'URL = "mysql://:memory:"' in content


def test_run_command(valid_steering_file, invalid_steering_file):
    runner = CliRunner()
    result = runner.invoke(mafw_exe.cli, ['run'])
    assert "Error: Missing argument 'STEERING_FILE'." in result.output

    result = runner.invoke(mafw_exe.cli, ['run', str(valid_steering_file)])
    assert 'Executing AccumulatorProcessor processor' in result.output

    result = runner.invoke(mafw_exe.cli, ['--log-level', 'debug', 'run', str(valid_steering_file)])
    assert 'Executing AccumulatorProcessor processor' in result.output
    assert 'DEBUG    AccumulatorProcessor is initializing' in result.output

    result = runner.invoke(mafw_exe.cli, ['run', str(invalid_steering_file)])
    assert 'ERROR    InvalidSteeringFile: Missing UserInterface' in result.output
    assert 'Traceback (most recent call last)' not in result.output

    result = runner.invoke(mafw_exe.cli, ['-D', 'run', str(invalid_steering_file)])
    assert 'ERROR    Missing section UserInterface' in result.output
    assert 'Traceback (most recent call last)' in result.output


def test_db_group():
    runner = CliRunner()
    result = runner.invoke(mafw_exe.cli, ['db'])
    # expect to read general help from db group
    assert 'Advanced database commands' in result.output


def test_wizard(shared_datadir, tmp_path):
    runner = CliRunner()
    # invoke without arguments
    result = runner.invoke(mafw_exe.cli, ['db', 'wizard'])
    assert "Error: Missing argument 'DATABASE'" in result.output

    # invoke with help
    result = runner.invoke(mafw_exe.cli, ['db', 'wizard', '-h'])
    assert 'mafw db wizard [Options] Database' in result.output

    output_file = tmp_path / 'my_db.py'
    input_database = shared_datadir / 'advanced_db.db'
    result = runner.invoke(mafw_exe.cli, ['db', 'wizard', '-o', str(output_file), str(input_database)])
    # check if output file has been created
    assert output_file.exists()

    # calculate checksum of such file for further use
    checksum = file_checksum(output_file)

    # rerun with no overwrite and cancel
    result = runner.invoke(
        mafw_exe.cli, ['db', 'wizard', '--no-overwrite', '-o', str(output_file), str(input_database)], input='c'
    )
    assert output_file.exists()
    assert checksum == file_checksum(output_file)

    # rerun with overwrite
    result = runner.invoke(mafw_exe.cli, ['db', 'wizard', '-o', str(output_file), str(input_database)])
    # check if output file has been created
    assert output_file.exists()
    assert result.exit_code == 0
    # the new file should be different because of the timestamp in the file
    assert checksum != file_checksum(output_file)
    # store the new checksum
    checksum = file_checksum(output_file)

    # rerun with overwrite and backup
    result = runner.invoke(
        mafw_exe.cli, ['db', 'wizard', '--no-overwrite', '-o', str(output_file), str(input_database)], input='b'
    )
    assert result.exit_code == 0
    # check if output file has been created
    assert output_file.exists()
    # the new file should be different because of the timestamp in the file
    assert checksum != file_checksum(output_file)
    # find the backup file
    pattern = str(output_file.stem) + '_*' + '.py'
    files = [p for p in Path(tmp_path).glob(pattern)]
    assert len(files) == 1
    bck_file = files[0]
    # check that the bckfile is the original file
    assert checksum == file_checksum(bck_file)

    # try to load the module. other tests are done in test_db_wizard.
    import sys

    sys.path.append(str(output_file.parent))
    try:
        import my_db  # noqa: I001, F401
    except ImportError:
        pytest.fail('Failed to import the generated model.')

    # try to give a wrong engine
    result = runner.invoke(
        mafw_exe.cli, ['db', 'wizard', '-e', 'wrongengine', '-o', str(output_file), str(input_database)]
    )
    assert result.exit_code != 0
    assert "Invalid value for '-e'" in result.output

    # try to run with a table subset
    result = runner.invoke(
        mafw_exe.cli, ['db', 'wizard', '-t', 'image', '-t', 'resolution', '-o', str(output_file), str(input_database)]
    )
    assert result.exit_code == 0
    # read back the module
    with open(output_file) as in_file:
        module = in_file.read()
    assert 'class Image(MAFwBaseModel):' in module
    assert 'class Resolution(MAFwBaseModel):' in module
    assert 'class Sample(MAFwBaseModel):' in module

    # try to run with a table subset w/o fk
    result = runner.invoke(
        mafw_exe.cli, ['db', 'wizard', '-t', 'sample', '-t', 'resolution', '-o', str(output_file), str(input_database)]
    )
    assert result.exit_code == 0
    # read back the module
    with open(output_file) as in_file:
        module = in_file.read()
    assert 'class Image(MAFwBaseModel):' not in module
    assert 'class Resolution(MAFwBaseModel):' in module
    assert 'class Sample(MAFwBaseModel):' in module

    # try to run with a table subset w/o fk and specific view
    result = runner.invoke(
        mafw_exe.cli,
        [
            'db',
            'wizard',
            '-t',
            'sample',
            '-t',
            'resolution',
            '-t',
            'image_view',
            '--with-views',
            '-o',
            str(output_file),
            str(input_database),
        ],
    )
    assert result.exit_code == 0
    # read back the module
    with open(output_file) as in_file:
        module = in_file.read()
    assert 'class Image(MAFwBaseModel):' not in module
    assert 'class Resolution(MAFwBaseModel):' in module
    assert 'class Sample(MAFwBaseModel):' in module
    assert 'class ImageView(MAFwBaseModel):' in module

    # try to run with all tables and views
    result = runner.invoke(mafw_exe.cli, ['db', 'wizard', '--with-views', '-o', str(output_file), str(input_database)])
    assert result.exit_code == 0
    # read back the module
    with open(output_file) as in_file:
        module = in_file.read()
    assert 'class ImageView(MAFwBaseModel):' in module
    assert 'class Resolution(MAFwBaseModel):' in module
    assert 'class Sample(MAFwBaseModel):' in module

    # preserved order
    sorted_class = """
class Image(MAFwBaseModel):
    image_id = AutoField()
    filename = TextField()
    checksum = TextField()
    sample = ForeignKeyField(column_name='sample_id', field='sample_id', model=Sample)
    resolution = ForeignKeyField(column_name='resolution_id', field='resolution_id', model=Resolution)"""

    # try to run with all tables with fields in alphabetical order
    result = runner.invoke(
        mafw_exe.cli, ['db', 'wizard', '--no-preserve-order', '-o', str(output_file), str(input_database)]
    )
    assert result.exit_code == 0
    # read back the module
    with open(output_file) as in_file:
        module = in_file.read()
    assert sorted_class not in module


def test_additional_processors_operation(tmp_path):
    @single_loop
    class Processor1(Processor):
        pass

    @single_loop
    class Processor2(Processor):
        pass

    # create a class container for the plugin hook
    class Container:
        @staticmethod
        @mafw_hookimpl
        def register_processors():
            return [Processor1, Processor2]

    pm = get_plugin_manager()
    pm.register(Container)

    available_processors_list = list(itertools.chain(*pm.hook.register_processors()))
    available_processors: dict[str, type[Processor]] = {p.__name__: p for p in available_processors_list}

    extra_processors = [p.__name__ for p in Container.register_processors()]
    for p in extra_processors:
        assert p in available_processors

    runner = CliRunner()
    result = runner.invoke(mafw_exe.cli, ['list'])
    for p in extra_processors:
        assert p in result.output

    # save a steering file with extra processors
    extra_steering_file = tmp_path / Path('extra_processor.toml')
    result = runner.invoke(mafw_exe.cli, ['steering', str(extra_steering_file)])

    # load the toml file
    toml_dict = TOMLFile(extra_steering_file).read().value
    available_processors_in_toml_file = toml_dict['available_processors']
    assert all([p in available_processors_in_toml_file for p in extra_processors])


def test_warning_catcher(shared_datadir, caplog):
    # create processors emitting warnings:
    class MissingMethodProcessor(Processor):
        # we do not implement the get_items
        pass

    @single_loop
    class MissingSuperProcessor(Processor):
        def start(self) -> None:
            i = 0  # noqa: F841

    class AnotherContainer:
        @staticmethod
        @mafw_hookimpl
        def register_processors():
            return [MissingMethodProcessor, MissingSuperProcessor]

    pm = get_plugin_manager()
    pm.register(AnotherContainer)

    warning_steering_file = shared_datadir / Path('warning_steering.toml')

    # execute the steering file with the two warning emitting processors.
    with pytest.warns((MissingOverloadedMethod, MissingSuperCall)):
        runner = CliRunner()
        result = runner.invoke(mafw_exe.cli, ['run', str(warning_steering_file)])
        assert result.exit_code == 0
