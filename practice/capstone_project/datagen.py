import argparse
import logging
import os
import queue
import random
import re
import sys
import json
import time
import uuid
import multiprocessing as mp
from configparser import ConfigParser
from typing import IO, Callable, Dict, Any, Generator, List

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


def validate_arguments(args: argparse.Namespace) -> argparse.Namespace:
    error = None
    if not os.path.isdir(args.path):
        error = f'not a valid path: {args.path}'
    if args.count < 0:
        error = f'files count is less than 0'
    if not args.name:
        error = f'file name cannot be empty'
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
        LOG.warning('number of processes exceeds number of cpu, defaults to number of cpu')
        args.multiprocessing = os.cpu_count()
    return args


def get_arguments(defaults: Dict[str, Any]) -> argparse.Namespace:
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
    return validate_arguments(p.parse_args())


def parse_data_timestamp(gen_type: str) -> Callable[[None], float]:
    if gen_type:
        LOG.warning('timestamp does not accept generation type, it will be ignored')
    return time.time


def parse_data_str(gen_type: str) -> Callable:
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


def parse_data_int(gen_type) -> Callable:
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


def parse_data_schema(raw_schema: str) -> Dict[str, Callable]:
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


def write_data_line(schema: Dict[str, Callable], fp: IO = sys.stdout) -> None:
    line = {k: v() for k, v in schema.items()}
    fp.write(json.dumps(line) + '\n')


def clear_path_with_files(name: str, path: str) -> None:
    for file in os.listdir(path):
        if file.endswith(name + '.jsonl'):
            os.remove(os.path.join(path, file))


def gen_file_name(prefix: str, base_name: str, count: int) -> Generator[str, None, None]:
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


def write_data_in_file(path: str, name: str, schema: Dict[str, Callable], lines: int) -> None:
    with open(os.path.join(path, name), 'w') as f:
        for i in range(lines):
            write_data_line(schema, f)


def write_data_mp_worker(task_queue: mp.JoinableQueue) -> None:
    while True:
        try:
            data = task_queue.get_nowait()
            write_data_in_file(*data)
        except queue.Empty:
            return


def write_data_mp(tasks: mp.JoinableQueue, processes: int) -> None:
    LOG.info(f'creating data in {processes} processes')
    process_pool = [mp.Process(target=write_data_mp_worker, args=(tasks, ))
                    for _ in range(processes)]
    [p.start() for p in process_pool]
    [p.join() for p in process_pool]
    [p.close() for p in process_pool]


def write_data(schema: Dict[str, Callable], args: argparse.Namespace) -> None:
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
        if processes == 1:
            for name in name_gen:
                write_data_in_file(path, name, schema, lines)
        else:
            tasks = mp.JoinableQueue()
            for name in name_gen:
                tasks.put((path, name, schema, lines))
            write_data_mp(tasks, processes)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(levelname)s: %(message)s')
    defaults = get_config()
    LOG.info('config found')
    args = get_arguments(defaults)
    LOG.info('arguments are correct')
    schema = get_schema(args.data_schema)
    LOG.info('data_schema parsed correctly')
    LOG.info('building datasets...')
    start = time.perf_counter()
    write_data(schema, args)
    LOG.info('done!')
    duration = time.perf_counter() - start
    LOG.info(f'data was written within {duration:.2f} seconds')
