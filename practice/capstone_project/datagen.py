import argparse
import logging
import os
import random
import re
import sys
import json
import time
import uuid
import multiprocessing as mp
from configparser import ConfigParser
from typing import IO, Callable, Dict, Any, Generator, List
from functools import partial

CONFIG_NAME = 'default.ini'
CLI_NAME = 'datagen'
LOG = logging.getLogger(CLI_NAME)


def get_config() -> Dict[str, Any]:
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


def validate_arguments(args: argparse.Namespace) -> None:
    error = None
    if not os.path.isdir(args.path):
        error = f'not a valid path: {args.path}'
    elif args.count < 0:
        error = 'files count is less than 0'
    elif not args.name:
        error = 'file name cannot be empty'
    if error:
        logging.error(error)
        sys.exit(1)

    if args.data_lines < 1:
        LOG.warning('less than 1 line of data was specified, defaults to 1')
        args.data_lines = 1
    if args.multiprocessing < 1:
        LOG.warning('number of processes cannot be < 1, defaults to 1')
        args.multiprocessing = 1
    if args.multiprocessing > os.cpu_count():
        LOG.warning('number of processes exceeds cpu number, defaults to number of cpu')
        args.multiprocessing = os.cpu_count()


def args_to_dict(args: argparse.Namespace) -> Dict:
    return dict(clear_path=args.clear_path,
                count=args.count,
                lines=args.data_lines,
                procs=args.multiprocessing,
                name=args.name,
                prefix=args.prefix,
                path=args.path,
                schema=args.data_schema)


def get_arguments(defaults: Dict) -> Dict:
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
    args = p.parse_args()
    validate_arguments(args)
    return args_to_dict(args)


def parse_data_timestamp(gen_type: str) -> Callable[[None], float]:
    if gen_type:
        LOG.warning('timestamp does not accept generation type, it will be ignored')
    return time.time


def callable_str_rand():
    return str(uuid.uuid4())


def callable_str_choice(values):
    return partial(random.choice, values)


def callable_str(string):
    return partial(str, string)


def parse_data_str(gen_type: str) -> Callable:
    if not gen_type:
        return str
    elif gen_type == 'rand':
        return callable_str_rand
    elif gen_type[0] == '[' and gen_type[-1] == ']':
        return callable_str_choice([str(val) for val in eval(gen_type)])
    elif re.match(r'rand\(\d+.*?\d+\)', gen_type):
        raise ValueError(f'generation type {gen_type} is valid only for integers')
    else:
        return callable_str(gen_type)


def callable_int_none():
    return None


def callable_int_rand():
    return partial(random.randint, 0, 10000)


def callable_int_choice(values):
    return partial(random.choice, values)


def callable_int_randint(n1, n2):
    return partial(random.randint, n1, n2)


def callable_int(integer):
    return partial(int, integer)


def parse_data_int(gen_type) -> Callable:
    if not gen_type:
        return callable_int_none
    elif gen_type == 'rand':
        return callable_int_rand()
    elif gen_type[0] == '[' and gen_type[-1] == ']':
        int_list = [int(n) for n in eval(gen_type)]
        return callable_int_choice(int_list)
    elif re.match(r'rand\(\d+.*?\d+\)', gen_type):
        int_list = [int(n) for n in re.findall(r'(\d+).*?(\d+)', gen_type)[0]]
        return callable_int_randint(*int_list)
    elif re.match(r'^[+-]*\d+$', gen_type):
        return callable_int(gen_type)
    else:
        raise ValueError(f'invalid generation type for integers: {gen_type}')


def extract_schema_from_json(raw_schema: str) -> Dict:
    try:
        if os.path.isfile(raw_schema):
            with open(raw_schema, 'r') as f:
                schema = json.load(fp=f)
        else:
            schema: dict = json.loads(raw_schema)
        if isinstance(schema, list):
            raise ValueError('data_schema must be a dict, decoded a list of dicts')
    except ValueError as exc:
        raise ValueError(f'JSON decoding failed: {exc}') from None
    else:
        return schema


def parse_data_schema(raw_schema: str) -> Dict[str, Callable]:
    schema = extract_schema_from_json(raw_schema)
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


def get_schema(raw_schema: str) -> Dict[str, Callable]:
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


def write_data_line(schema: Dict, fp: IO = sys.stdout) -> None:
    line = {k: v() for k, v in schema.items()}
    fp.write(json.dumps(line) + '\n')


def clear_path_with_files(name: str, path: str) -> None:
    for file in os.listdir(path):
        if file.endswith(name + '.jsonl'):
            os.remove(os.path.join(path, file))


def gen_file_name(prefix: str, base_name: str, count: int) -> Generator:
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


def write_data_in_file(path: str, name: str, schema: Dict, lines: int) -> None:
    with open(os.path.join(path, name), 'w') as f:
        for i in range(lines):
            write_data_line(schema, f)


def write_data_mp(tasks: List, processes: int) -> None:
    with mp.Pool(processes=processes) as pool:
        pool.starmap(write_data_in_file, tasks)


def write_data(schema: Dict, args: Dict) -> None:
    if args['count'] == 0:
        for line in range(args['lines']):
            write_data_line(schema)
    else:
        if args['clear_path']:
            clear_path_with_files(args['name'], args['path'])
        name_gen = gen_file_name(args['prefix'], args['name'], args['count'])
        if args['procs'] == 1:
            LOG.info('writing data in 1 process...')
            for name in name_gen:
                write_data_in_file(args['path'], name, schema, args['lines'])
        else:
            LOG.info(f'writing data in {args["procs"]} processes...')
            tasks = [(args['path'], name, schema, args['lines'])
                     for name in name_gen]
            write_data_mp(tasks, args['procs'])


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(levelname)s: %(message)s')
    default_args = get_config()
    LOG.info('config found')

    arguments = get_arguments(default_args)
    LOG.info('arguments are correct')

    data_schema = get_schema(arguments['schema'])
    LOG.info('data_schema parsed successfully')

    LOG.info('begin generating files')
    start = time.perf_counter()
    write_data(data_schema, arguments)
    LOG.info('done!')

    duration = time.perf_counter() - start
    LOG.info(f'data was written within {duration:.2f} seconds')


if __name__ == '__main__':
    main()
