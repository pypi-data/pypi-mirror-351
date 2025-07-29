from pathlib import Path, PosixPath, WindowsPath

import pytest
import tomlkit.exceptions
from tomlkit.toml_file import TOMLFile

import mafw.mafw_errors
import mafw.tools.toml_tools
from mafw.db.db_configurations import default_conf
from mafw.decorators import single_loop
from mafw.processor import ActiveParameter, PassiveParameter, Processor
from mafw.tools.toml_tools import (
    _add_db_configuration,
    dump_processor_parameters_to_toml,
    generate_steering_file,
    load_steering_file,
)


@single_loop
class ActiveParameterProcessor(Processor):
    """A processor with one active parameter."""

    active_param = ActiveParameter('active_param', default=-1, help_doc='An active parameter with default value -1')


@single_loop
class AnotherActiveParameterProcessor(Processor):
    """Another processor with one active parameter."""

    active_param = ActiveParameter('active_param', default=-1, help_doc='An active parameter with default value -1')


class PassiveParameterProcessor(Processor):
    """A processor with one passive parameter."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, looper='single', **kwargs)
        self.passive_param = PassiveParameter(
            'passive_param', default=-1, help_doc='A passive parameter with default value -1'
        )


class AnotherPassiveParameterProcessor(Processor):
    """Another processor with one passive parameter."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, looper='single', **kwargs)
        self.passive_param = PassiveParameter(
            'passive_param', default=-1, help_doc='A passive parameter with default value -1'
        )


@pytest.fixture
def registered_example_processor() -> list[type[Processor]]:
    from mafw.examples.loop_modifier import ModifyLoopProcessor
    from mafw.examples.sum_processor import AccumulatorProcessor, GaussAdder

    return [AccumulatorProcessor, GaussAdder, ModifyLoopProcessor]


def get_toml(input_file: str | Path) -> dict:
    return TOMLFile(input_file).read().value


def test_wrong_type():
    output_file_example = 'test1.toml'
    with pytest.raises(TypeError):
        processor_list = [
            ActiveParameterProcessor,
            ActiveParameterProcessor,
            'a string',
            PassiveParameterProcessor,
            AnotherActiveParameterProcessor,
        ]
        dump_processor_parameters_to_toml(processor_list, output_file_example)

    Path(output_file_example).unlink(missing_ok=True)


def test_same_name_exception():
    output_file_example = 'test1.toml'
    with pytest.raises(tomlkit.exceptions.KeyAlreadyPresent) as e:
        processor_list = [
            ActiveParameterProcessor,
            ActiveParameterProcessor,
            PassiveParameterProcessor,
            AnotherActiveParameterProcessor,
        ]
        dump_processor_parameters_to_toml(processor_list, output_file_example)
    assert 'ActiveParameterProcessor' in str(e.value)
    Path(output_file_example).unlink(missing_ok=True)


def test_dump_processor_parameters_to_toml_1(datadir, tmp_path):
    output_file_example = 'test1.toml'

    processor_list = [
        ActiveParameterProcessor,
        AnotherPassiveParameterProcessor,
        PassiveParameterProcessor,
        AnotherActiveParameterProcessor,
    ]

    dump_processor_parameters_to_toml(processor_list, tmp_path / output_file_example)

    expected_output_file = datadir / f'expected_{output_file_example}'
    expected_dict = get_toml(expected_output_file)
    obtained_dict = get_toml(tmp_path / output_file_example)

    # the dictionaries are as expected
    assert expected_dict == obtained_dict

    # the text file is identical
    with open(tmp_path / output_file_example) as fp:
        generated_file = fp.readlines()

    with open(expected_output_file) as fp:
        expected_file = fp.readlines()

    # skip the first line because there is timestamp
    assert generated_file[1:] == expected_file[1:]


def test_steering_file_generation_with_no_db(datadir, tmp_path, registered_example_processor):
    output_file_example = 'steering-file.toml'
    generate_steering_file(tmp_path / output_file_example, registered_example_processor)

    expected_output_file = datadir / f'generated-{output_file_example}'
    expected_dict = get_toml(expected_output_file)
    obtained_dict = get_toml(tmp_path / output_file_example)

    # the dictionaries should have the same keys
    assert list(expected_dict.keys()) == list(obtained_dict.keys())
    # values might be different depending on previous tests.


def test_dump_processor_parameters_to_toml_2(datadir, tmp_path):
    output_file_example = 'test2.toml'

    # create an instance of ActiveParameterProcessor with a specific value of the parameter
    # but we will include the class in the processor list.
    ActiveParameterProcessor(active_param=100)

    # create an instance of AnotherActiveParameterProcessor with a specific value of the parameter
    # and we will submit the instance
    another_active_processor_instance = AnotherActiveParameterProcessor(active_param=101)

    # create an instance of PassiveParameterProcessor with a specific value of the parameter
    # but we will submit the class via the use of type.
    passive_processor_instance = PassiveParameterProcessor(passive_param=102)

    # create an instance of AnotherPassiveParameterProcessor with a specific value of the parameter
    # and we will submit the instance.
    another_passive_processor_instance = AnotherPassiveParameterProcessor(passive_param=103)

    processor_list = [
        ActiveParameterProcessor,  # a class
        another_active_processor_instance,  # an instance
        type(passive_processor_instance),  # a class
        another_passive_processor_instance,  # an instance
    ]
    dump_processor_parameters_to_toml(processor_list, tmp_path / output_file_example)
    expected_output_file = datadir / f'expected_{output_file_example}'
    expected_dict = get_toml(expected_output_file)
    obtained_dict = get_toml(tmp_path / output_file_example)

    # the dictionaries are as expected
    assert expected_dict == obtained_dict

    # the text file is identical
    with open(tmp_path / output_file_example) as fp:
        generated_file = fp.readlines()

    with open(expected_output_file) as fp:
        expected_file = fp.readlines()

    # skip the first line because there is timestamp
    assert generated_file[1:] == expected_file[1:]


def test_load_steering_file():
    with pytest.raises(FileNotFoundError) as e:
        load_steering_file('pippo')
    assert 'pippo' in str(e.value)


def test_validating_steering_file(datadir):
    valid_file = 'valid-steering-file.toml'
    load_steering_file(datadir / valid_file)

    invalid_files = range(1, 3)
    for i in invalid_files:
        invalid_file = f'invalid-steering-file{i}.toml'
        with pytest.raises(mafw.mafw_errors.InvalidSteeringFile):
            load_steering_file(datadir / invalid_file)


def test_add_db_configuration(caplog):
    # test exception raise with no conf and unknown engine
    with pytest.raises(mafw.mafw_errors.UnknownDBEngine) as e:
        _add_db_configuration(db_engine='unknown')
    assert 'unknown' in str(e.value)
    assert '(unknown) is not yet implemented' in caplog.text
    caplog.clear()

    # test exception raise with unknown engine and invalid configuration
    conf = {'invalid': 'invalid'}
    with pytest.raises(mafw.mafw_errors.UnknownDBEngine) as e:
        _add_db_configuration(database_conf=conf, db_engine='unknown')
    assert len(caplog.records) == 2
    assert 'The provided database configuration is invalid.' in caplog.text
    assert '(unknown) is not yet implemented' in caplog.text
    caplog.clear()

    # test log message with known engine and invalid configuration
    engine = 'mysql'
    doc = _add_db_configuration(database_conf=conf, db_engine=engine)
    assert 'The provided database configuration is invalid. Adding default configuration' in caplog.text
    assert doc.value['DBConfiguration'] == default_conf[engine]
    caplog.clear()

    # test log message with invalid configuration and no explict db_engine
    doc = _add_db_configuration(database_conf=conf)
    assert 'The provided database configuration is invalid. Adding default configuration' in caplog.text
    assert doc.value['DBConfiguration'] == default_conf['sqlite']
    caplog.clear()


def test_path_encoding():
    obj = {'path': Path.cwd()}
    doc = tomlkit.dumps(obj)
    if isinstance(Path.cwd(), WindowsPath):
        assert doc == f"""path = '{str(Path.cwd())}'\n"""
    elif isinstance(Path, PosixPath):
        assert doc == f"""path = "{str(Path.cwd())}"\n"""
