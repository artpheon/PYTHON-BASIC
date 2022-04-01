import argparse
import logging
import os
import random
import re
import sys
import json
import time
import uuid
from configparser import ConfigParser
from concurrent.futures import ProcessPoolExecutor
from typing import Iterable, IO

CONFIG_NAME = 'default.ini'
CLI_NAME = 'datagen'
LOG = logging.getLogger(CLI_NAME)


def setup_logger():
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(levelname)s: %(message)s')


def get_config() -> dict:
    cp = ConfigParser()
    try:
        if not cp.read(CONFIG_NAME):
            raise ValueError(f'could not read file: {CONFIG_NAME}')
        section = cp['default']
        items = dict(path=section['path'],
                     count=section.getint('count'),
                     name=section['name'],
                     prefix=section['prefix'],
                     data_schema=section['data_schema'],
                     data_lines=section.getint('data_lines'),
                     clear_path=section.getboolean('clear_path'),
                     multiprocessing=section.getint('multiprocessing'))
    except ValueError as exc:
        LOG.error(exc)
    except Exception as exc:
        LOG.error(f'error while extracting values from {CONFIG_NAME}: {exc}')
    else:
        return items
    sys.exit(1)


def get_arguments(defaults: dict) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog=CLI_NAME,
                                description='This tool helps generate JSON datasets.',
                                add_help=True)
    p.add_argument('-p', '--path', action='store', type=str,
                   help='Add path, for the generated files to be saved.',
                   default=defaults['path'])
    p.add_argument('-c', '--count', action='store', type=int,
                   help='Number of JSON files to generate.',
                   default=defaults['count'])
    p.add_argument('-n', '--name', action='store', type=str,
                   help='Set file base name.', default=defaults['name'])
    p.add_argument('-pr', '--prefix', action='store', type=str,
                   choices=['count', 'random', 'uuid'],
                   help='Set file prefix for files count > 1.',
                   default=defaults['prefix'])
    p.add_argument('-ds', '--data_schema', action='store', type=str,
                   help='Data schema for building data.',
                   default=defaults['data_schema'])
    p.add_argument('-dl', '--data_lines', action='store', type=int,
                   help='Set number of lines of data in a file.',
                   default=defaults['data_lines'])
    p.add_argument('-cp', '--clear_path', action='store_false',
                   help='Before generating the data, all files in PATH, with name NAME'
                        ' will be deleted',
                   default=defaults['clear_path'])
    p.add_argument('-mp', '--multiprocessing', action='store', type=int,
                   help='Set the number of processes to generate the data.',
                   default=defaults['multiprocessing'])
    #  todo validate negative numbers
    return p.parse_args()


def parse_data_timestamp(gen_type):
    if gen_type:
        LOG.warning('timestamp does not accept generation type, it will be ignored')
    return time.time


def parse_data_str(gen_type):
    if not gen_type:
        return str
    elif gen_type == 'rand':
        return lambda: str(uuid.uuid4())
    elif gen_type[0] == '[' and gen_type[-1] == ']':
        return lambda: str(random.choice(eval(gen_type)))
    elif re.match(r'rand\(\d+.*?\d+\)', gen_type):
        raise ValueError(f'generation type {gen_type} is valid only for integers')
    else:
        return lambda: str(gen_type)


def parse_data_int(gen_type):
    if not gen_type:
        return lambda: None
    elif gen_type == 'rand':
        return lambda: random.randint(0, 10000)
    elif gen_type[0] == '[' and gen_type[-1] == ']':
        int_list = [int(n) for n in eval(gen_type)]
        return lambda: random.choice(int_list)
    elif re.match(r'rand\(\d+.*?\d+\)', gen_type):
        int_list = [int(n) for n in re.findall(r'(\d+).*?(\d+)', gen_type)[0]]
        return lambda: random.randint(*int_list)
    elif re.match(r'^[+-]\d+$', gen_type):
        return lambda: int(gen_type)
    else:
        raise ValueError(f'invalid generation type for integers: {gen_type}')


def parse_data_schema(raw_schema: str) -> dict:
    schema: dict = json.loads(raw_schema)
    parser = dict(timestamp=parse_data_timestamp, str=parse_data_str, int=parse_data_int)
    for k, v in schema.items():
        value = v.split(':')
        if len(value) != 2:
            raise SyntaxError(f'{v} in schema must be in "argument_type:generation_type"'
                              f' format')
        arg_type, gen_type = value
        if arg_type not in parser:
            raise ValueError(f'{arg_type} is invalid argument type')
        schema[k] = parser[arg_type](gen_type)
    return schema


def get_schema(raw_schema):
    try:
        schema = parse_data_schema(raw_schema)
    except ValueError as exc:
        LOG.error(exc)
    except SyntaxError as exc:
        LOG.error(exc)
    except Exception as exc:
        LOG.error(f'unexpected error: {exc}')
    else:
        return schema
    sys.exit(1)


def write_data_line(schema: dict, fp: IO = sys.stdout):
    line = {k: v() for k, v in schema.items()}
    fp.write(json.dumps(line) + '\n')


def clear_path_with_files(name: str, path: str):
    for file in os.listdir(path):
        if file.endswith(name + '.jsonl'):
            os.remove(os.path.join(path, file))


def gen_file_name(prefix: str, base_name: str, count):
    if prefix == 'count':
        for i in range(count):
            yield f'{i + 1}_{base_name}.jsonl'
    elif prefix == 'rand':
        import string
        for i in range(count):
            x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            yield f'{x}_{base_name}.jsonl'
    else:
        for i in range(count):
            yield f'{uuid.uuid4()}_{base_name}.jsonl'


def write_data_in_file(path, name, schema, lines):
    with open(os.path.join(path, name), 'w') as f:
        for i in range(lines):
            write_data_line(schema, f)


def write_data(schema: dict, args: argparse.Namespace):
    clear_path = args.clear_path
    count = args.count
    lines = args.data_lines
    processes = args.multiprocessing
    name = args.name
    prefix = args.prefix
    path = args.path
    if count == 0:
        for line in range(lines):
            write_data_line(schema)
    else:
        if clear_path:
            clear_path_with_files(name, path)
        name_gen = gen_file_name(prefix, name, count)
        for name in name_gen:
            write_data_in_file(path, name, schema, lines)


if __name__ == '__main__':
    setup_logger()
    defaults = get_config()
    LOG.info('config found')
    args = get_arguments(defaults)
    LOG.info('arguments are correct')
    schema = get_schema(args.data_schema)
    LOG.info('data_schema parsed correctly')
    write_data(schema, args)
