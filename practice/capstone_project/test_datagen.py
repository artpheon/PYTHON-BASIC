import os
import sys
import pytest
from datagen import get_config, get_arguments, get_schema, write_data
from typing import Callable
from pathlib import Path


TEST_CONFIG = [
    (['datagen.py', '-p=.', '-c=1', '-n=file', '-pr=count', '-dl=1', '-cp', '-mp=1'], False),
    (['datagen.py', '-p=../nosuchpath', '-c=1', '-n=file', '-pr=count', '-dl=1', '-cp', '-mp=1'], True),
    (['datagen.py', '-p=.', '-c=string', '-n=file', '-pr=count', '-dl=1', '-cp', '-mp=1'], True),
    (['datagen.py', '-p=.', '-c=-1', '-n=file', '-pr=count', '-dl=1', '-cp', '-mp=1'], True),
    (['datagen.py', '-p=.', '-c=1', '-n=', '-pr=count', '-dl=1', '-cp', '-mp=1'], True),
    (['datagen.py', '-p=.', '-c=1', '-n=file', '-pr=different', '-dl=1', '-cp', '-mp=1'], True),
    (['datagen.py', '-p=.', '-c=1', '-n=file', '-pr=count', '-dl=string', '-cp', '-mp=1'], True),
    (['datagen.py', '-p=.', '-c=1', '-n=file', '-pr=count', '-dl=1', '-cp', '-mp=string'], True),
]

TEST_SCHEMAS = [
    ('{"date": "timestamp:", "text": "str:string"}', False),
    ('{"date": "timestamp:something", "text": "str:string"}', False),
    ('{"text": "str:rand"}', False),
    ('{"text": "str:[\'some\', \'strings\']"}', False),
    ('{"text": "str:"}', False),
    ('{"text": "str:rand(0, 5)"}', True),
    ('{"integers": "int:"}', False),
    ('{"integers": "int:5"}', False),
    ('{"integers": "int:rand(0, 5)"}', False),
    ('{"integers": "int:rand"}', False),
    ('{"integers": "int:[1, 2, 3, 4]"}', False),
    ('{"integers": "int:[\'some\', \'strings\']"}', True),
    ('{"integers": "int:string"}', True),
]

TEST_SCHEMAS_FILE = [
    ('{"date":"timestamp:", "name": "str:rand", "type":"str:[\'client\', \'partner\', \'government\']"}',
     ['date', 'name', 'type']),
    ('{"value":"int:", "integer": "int:5", "choice":"int:[1, 2, 3, 4, 5]"}',
     ['value', 'integer', 'choice']),
]

TEST_SCHEMAS_WRITE = [
    (5, 'file', 5),
    (10, 'super', 10),
    (12, 'new_file_data', 1)
]

TEST_MULTIPROC = [
    (3, 3),
    (5, 10),
    (1, 20),
    (2, 145),
    (30, 2)
]


def test_basic_config():
    conf = get_config()
    assert isinstance(conf, dict)
    assert 'path' in conf
    assert 'count' in conf
    assert 'name' in conf
    assert 'prefix' in conf
    assert 'data_schema' in conf
    assert 'data_lines' in conf
    assert 'clear_path' in conf
    assert 'multiprocessing' in conf


@pytest.mark.parametrize("arguments, raises", TEST_CONFIG)
def test_basic_config_err(arguments: list, raises: bool):
    sys.argv = arguments
    defaults = get_config()
    if raises:
        with pytest.raises(expected_exception=SystemExit):
            get_arguments(defaults)
    else:
        assert get_arguments(defaults) is not None


@pytest.mark.parametrize("schema, raises", TEST_SCHEMAS)
def test_schemas(schema, raises):
    if raises:
        with pytest.raises(SystemExit):
            assert get_schema(schema) is not None
    else:
        assert get_schema(schema) is not None


@pytest.mark.parametrize('schema, attrs', TEST_SCHEMAS_FILE)
def test_schemas_json_file(tmp_path, schema, attrs):
    d = tmp_path / 'tmpdir'
    d.mkdir()
    f = d / 'schema.json'
    f.write_text(schema)
    assert f.read_text() == schema
    data_schema = get_schema(f.as_posix())
    assert data_schema is not None
    for attr in attrs:
        assert attr in data_schema
    for v in data_schema.values():
        assert isinstance(v, Callable)


def test_clear_path(tmp_path):
    def write_and_get_files(schema, args):
        write_data(schema, args)
        files = os.listdir(args['path'])
        file_data = set()
        for file in files:
            with open(os.path.join(args['path'], file), 'r') as f:
                file_data.add(f.read())
        return files, file_data

    d = tmp_path / 'tmp_directory'
    d.mkdir()
    path = d.as_posix()
    sys.argv = ['datagen.py', f'-p={path}', '-c=5', '-n=file', '-pr=count', '-dl=5', '-cp', '-mp=1']
    defaults = get_config()
    args = get_arguments(defaults)
    schema = get_schema(args['schema'])
    assert not os.listdir(path)
    files_1, files_data_1 = write_and_get_files(schema, args)
    files_2, files_data_2 = write_and_get_files(schema, args)
    assert set(files_1) == set(files_2)
    assert files_data_1 != files_data_2


def execute(sys_argv):
    sys.argv = sys_argv
    defaults = get_config()
    args = get_arguments(defaults)
    schema = get_schema(args['schema'])
    write_data(schema, args)


@pytest.mark.parametrize('count,fname,lines', TEST_SCHEMAS_WRITE)
def test_saving_files(tmp_path, count, fname, lines):
    d = tmp_path / 'tmp_dir'
    d.mkdir()
    path = d.as_posix()
    execute(['datagen.py', f'-p={path}', f'-c={count}', f'-n={fname}', '-pr=count', f'-dl={lines}', '-cp'])
    files = os.listdir(path)
    assert len(files) == count
    for file in files:
        assert fname in file
        with open(os.path.join(path, file), 'r') as f:
            assert len(f.readlines()) == lines


@pytest.mark.parametrize('count,processes', TEST_MULTIPROC)
def test_multiproc_write(tmp_path, count, processes):
    d = tmp_path / 'tmp_dir'
    d.mkdir()
    path = d.as_posix()
    execute(['datagen.py', f'-p={path}', f'-c={count}', '-cp', f'-mp={processes}'])
    assert count == len(os.listdir(path))
