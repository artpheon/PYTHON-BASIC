import sys
from datagen import get_config, get_arguments, get_schema, write_data
import pytest
from pathlib import Path


TEST_CONFIG = [
    (['-p=.', '-c=1', '-n=file', '-pr=count', '-dl=1', '-cp', '-mp=1'], False),
    (['-p=../nosuchpath', '-c=1', '-n=file', '-pr=count', '-dl=1', '-cp', '-mp=1'], False),
    (['-p=.', '-c=string', '-n=file', '-pr=count', '-dl=1', '-cp', '-mp=1'], True),
    (['-p=.', '-c=-1', '-n=file', '-pr=count', '-dl=1', '-cp', '-mp=1'], True),
    (['-p=.', '-c=1', '-n=', '-pr=count', '-dl=1', '-cp', '-mp=1'], True),
    (['-p=.', '-c=1', '-n=file', '-pr=different', '-dl=1', '-cp', '-mp=1'], True),
    (['-p=.', '-c=1', '-n=file', '-pr=count', '-dl=string', '-cp', '-mp=1'], True),
    (['-p=.', '-c=1', '-n=file', '-pr=count', '-dl=1', '-cp', '-mp=string'], True),
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


def test_schemas_json_file(tmp_path):
    pass