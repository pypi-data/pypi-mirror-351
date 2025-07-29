import itertools
import os
import random
import re
import tomllib
from pathlib import Path

import pytest
from click.testing import CliRunner
from playhouse.db_url import connect
from tomlkit.toml_file import TOMLFile

from mafw.db.db_model import database_proxy
from mafw.examples.importer_example import InputElement
from mafw.mafw_errors import MissingAttribute, ParserConfigurationError, ParsingError
from mafw.processor_library.importer import FilenameElement, FilenameParser
from mafw.scripts import mafw_exe


def test_filename_element_creation():
    name = 'sample_name'
    str_pattern = f'(?P<{name}>' + r'sample_[\d]{1,5})'

    # creation with a string pattern
    fe = FilenameElement(name, str_pattern)
    assert not fe.is_optional
    assert not fe.is_found
    assert fe.pattern == str_pattern
    assert fe.name == name
    assert fe.value is None
    assert fe._default_value == fe.value

    # creation with a compile str re
    str_regexp = re.compile(str_pattern)
    fe = FilenameElement(name, str_regexp)
    assert not fe.is_optional
    assert not fe.is_found
    assert fe.pattern == str_pattern
    assert fe.name == name
    assert fe.value is None
    assert fe._default_value == fe.value

    ### failed creation
    for r in [str_pattern, str_regexp]:
        with pytest.raises(ValueError, match='a named group'):
            FilenameElement('wrong_name', r)

    # test creation with default value
    default = 'A'
    # creation with a string pattern
    fe = FilenameElement(name, str_pattern, default_value=default)
    assert fe.is_optional
    assert fe.is_found
    assert fe.pattern == str_pattern
    assert fe.name == name
    assert fe.value == default
    assert fe._default_value == fe.value

    fe = FilenameElement(name, str_regexp, default_value=default)
    assert fe.is_optional
    assert fe.is_found
    assert fe.pattern == str_pattern
    assert fe.name == name
    assert fe.value == default
    assert fe._default_value == fe.value

    # creation of a filename element with a default value not matching the value type
    default = 1
    for p in [str_pattern, str_regexp]:
        with pytest.raises(TypeError, match='(int)'):
            # default type is int, value type is not provided so it should be str
            FilenameElement(name, p, default_value=default)

    value_type = float
    for p in [str_pattern, str_regexp]:
        with pytest.raises(TypeError, match='(float)'):
            # default type is int, value type is float. That is rather tricky
            FilenameElement(name, p, default_value=default, value_type=value_type)

    # test successful search
    elements = ['sample_12345', Path('sample_453')]
    regexps = [str_pattern, str_regexp]
    for p in regexps:
        sne = FilenameElement(name, p)
        for e in elements:
            assert sne.value is None
            sne.search(e)
            assert sne.is_found
            assert sne.value == str(e)
            sne.reset()
            assert sne.value is None

    # test successful search with default
    for p in regexps:
        sne = FilenameElement(name, p, default_value='sample_8888')
        for e in elements:
            assert sne.value == 'sample_8888'
            sne.search(e)
            assert sne.is_found
            assert sne.value == str(e)
            sne.reset()
            assert sne.value == 'sample_8888'

    # test failing search
    elements = ['sample_test', Path('sample_another')]
    for p in regexps:
        sne = FilenameElement(name, p)
        for e in elements:
            assert sne.value is None
            sne.search(e)
            assert not sne.is_found
            assert sne.value is None
            sne.reset()
            assert sne.value is None

    # test failing search with default
    for p in regexps:
        sne = FilenameElement(name, p, default_value='sample_8888')
        for e in elements:
            assert sne.value == 'sample_8888'
            sne.search(e)
            assert sne.is_found  # when a default value is provided, the is_found is always true
            assert sne.value == 'sample_8888'
            sne.reset()
            assert sne.value == 'sample_8888'

    # test creation from conf dictionary
    good_confs = [{'regexp': str_regexp.pattern, 'type': 'str'}, {'regexp': str_pattern, 'type': 'int', default: 2}]
    for conf in good_confs:
        FilenameElement.from_dict(name=name, info_dict=conf)

    wrong_confs = [
        {'regexp': str_pattern, 'type': 'no_type'},
        {'regexp': 1213},
        {'regexp': str_regexp.pattern, 'type': str},
        {'reg_exp': str_pattern},
    ]
    for conf in wrong_confs:
        with pytest.raises((TypeError, ValueError, KeyError)):
            FilenameElement.from_dict(name=name, info_dict=conf)


def test_filename_parser(datadir):
    valid_configuration_file = datadir / Path('valid_parser_configuration.toml')

    # load the toml file
    with open(valid_configuration_file, 'rb') as fd:
        valid_configuration_toml_object = tomllib.load(fd)

    # test creation of a filename parser without specifying a filename
    fnp = FilenameParser(valid_configuration_file)
    assert fnp._filename is None
    assert len(fnp.elements) == len(valid_configuration_toml_object['elements'])
    assert all([e in valid_configuration_toml_object['elements'] for e in fnp.elements])

    with pytest.raises(MissingAttribute, match='filename'):
        fnp.interpret()

    # test creation of a filename parser with specifying a filename
    good_filename = 'A121-2011-0001_ci001_pBAS_pn1-r25u_exp1h.tiff'
    missing_element_filename = 'A121-2011-0001_ci001_pBAS_pn1-r25u.tiff'
    fnpw = FilenameParser(valid_configuration_file, filename=good_filename)
    assert fnpw._filename is good_filename
    assert len(fnpw.elements) == len(valid_configuration_toml_object['elements'])
    assert all([e in valid_configuration_toml_object['elements'] for e in fnpw.elements])

    with pytest.raises(ParsingError, match='exposure'):
        fnp.interpret(missing_element_filename)

    fnpw.interpret()
    fnp.interpret(good_filename)

    assert fnp.get_element_value('exposure') == 1
    assert fnp.get_element_value('wrong') is None

    assert isinstance(fnp.get_element('exposure'), FilenameElement)
    exp = fnp.get_element('exposure')
    assert exp.value == 1
    assert exp.pattern == valid_configuration_toml_object['exposure']['regexp']

    no_existing = fnpw.get_element('whatever')
    assert no_existing is None

    invalid_configuration_file = datadir / Path('invalid_parser_configuration.toml')
    with pytest.raises(ParserConfigurationError, match='sample_name'):
        FilenameParser(invalid_configuration_file)


def generate_element_files(filename_list, base_path, min_size=512, max_size=1024):
    for f in filename_list:
        full_path = Path(base_path) / Path(f)
        file_size = random.randint(min_size, max_size)
        with open(full_path, 'wb') as f_out:
            f_out.write(os.urandom(file_size))


def test_full_importer_example(tmp_path, datadir):
    input_folder = tmp_path / Path('data')
    input_folder.mkdir(exist_ok=True)

    # first let's generate some test files
    samples = [f'sample_{i:03}' for i in range(0, 5)]
    exposures = [f'exp{e / 2:.1f}h' for e in range(1, 5)]
    resolutions = [f'r{r}u' for r in [25, 50, 100]]
    full_filenames = [f'{"_".join(p)}.tif' for p in itertools.product(samples, exposures, resolutions)]
    default_filenames = [f'{"_".join(p)}.tif' for p in itertools.product(samples, exposures)]
    total_files = len(full_filenames + default_filenames)
    generate_element_files(full_filenames + default_filenames, input_folder)

    # read the importer steering file and modify the files and folders
    steering_doc = TOMLFile(datadir / Path('importer_example_steering.toml')).read()

    db_file = tmp_path / Path('test.db')
    db_file = 'sqlite:///' + str(db_file)
    steering_doc['DBConfiguration']['URL'] = db_file

    # this is the input folder
    steering_doc['ImporterExample']['input_folder'] = str(input_folder)

    # this is the parser configuration
    parser_conf = datadir / Path('importer_example_parser_conf.toml')
    steering_doc['ImporterExample']['parser_configuration'] = str(parser_conf)

    steering_file = tmp_path / Path('importer.toml')
    modified_file = TOMLFile(steering_file)
    modified_file.write(steering_doc)

    # read to run the mafw
    runner = CliRunner()
    result = runner.invoke(mafw_exe.cli, ['run', str(steering_file)])
    assert result.exit_code == 0

    # open the database locally
    database = connect(db_file)
    database_proxy.initialize(database)

    assert InputElement.select().count() == total_files

    # remove a few elements
    to_be_removed = InputElement.select().where(InputElement.resolution == 25).count()
    InputElement.delete().where(InputElement.resolution == 25).execute()
    assert InputElement.select().count() == total_files - to_be_removed

    database.close()

    # run the mafw again
    result = runner.invoke(mafw_exe.cli, ['run', str(steering_file)])
    assert result.exit_code == 0

    # open the database locally and counts the elements
    database = connect(db_file)
    database_proxy.initialize(database)
    assert InputElement.select().count() == total_files
    database.close()

    # modify the steering file to change the GlobalFilter new_only to False
    steering_file_doc = TOMLFile(steering_file).read()
    steering_file_doc['GlobalFilter']['new_only'] = False
    TOMLFile(steering_file).write(steering_file_doc)

    # run the mafw again
    result = runner.invoke(mafw_exe.cli, ['run', str(steering_file)])
    assert result.exit_code == 0

    # open the database locally and counts the elements
    database = connect(db_file)
    database_proxy.initialize(database)
    assert InputElement.select().count() == total_files
    database.close()


def test_for_general_doc(datadir):
    # start here
    filename = 'sample_12_energy_10_repetition_2.dat'

    sample = FilenameElement('sample', r'[_]*(?P<sample>sample_\d+)[_]*', value_type=str)
    energy = FilenameElement('energy', r'[_]*energy_(?P<energy>\d+\.*\d*)[_]*', value_type=float)
    repetition = FilenameElement(
        'repetition', r'[_]*repetition_(?P<repetition>\d+)[_]*', value_type=int, default_value=1
    )

    sample.search(filename)
    assert sample.value == 'sample_12'

    energy.search(filename)
    assert energy.value == 10

    repetition.search(filename)
    assert repetition.value == 2
    # finish here

    filename = 'energy_10.3_sample_12.dat'

    sample.search(filename)
    assert sample.value == 'sample_12'

    energy.search(filename)
    assert energy.value == 10.3

    repetition.search(filename)
    assert repetition.value == 1

    conf_file_name = datadir / Path('example_conf.toml')

    # filenameparser start
    filename = 'energy_10.3_sample_12.dat'

    parser = FilenameParser(conf_file_name)
    parser.interpret(filename)

    assert parser.get_element_value('sample') == 'sample_12'
    assert parser.get_element_value('energy') == 10.3
    assert parser.get_element_value('repetition') == 1
    # filenameparser end
