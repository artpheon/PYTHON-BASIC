import os
from random import randint
from time import perf_counter
import re
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

OUTPUT_DIR = './output'
RESULT_FILE = './output/result.csv'
MAX_PROC = os.cpu_count()
MAX_THREADS = min(32, MAX_PROC + 4)


def fib(n: int):
    """Calculate a value in the Fibonacci sequence by ordinal number"""

    f0, f1 = 0, 1
    for _ in range(n-1):
        f0, f1 = f1, f0 + f1
    return f1


# def get_values_from_array(array: list):
#     with ProcessPoolExecutor(max_workers=MAX_PROC) as executor:
#         result = executor.map(fib, array)
#         executor.map(write_one_value, zip(array, result))
#     # return zip(array, result)
#
#
def write_one_value(value):
    with open(f'{OUTPUT_DIR}/file {value[0]}.txt', 'w') as f:
        f.write(str(value[1]))
#
#
# def write_values_to_files(values: zip):
#     with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
#         executor.map(write_one_value, values)

#
# def func1(array: list):
#     result = get_values_from_array(array)
#     # write_values_to_files(result)


def func1(array: list):
    with ProcessPoolExecutor(max_workers=MAX_PROC) as executor:
        result = executor.map(fib, array)
        executor.map(write_one_value, zip(array, result))

# def func2(result_file: str):
#     files = os.listdir(OUTPUT_DIR)
#     with open(result_file, 'w') as result:
#         result.write('ordinal,fib\n')
#         for file in files:
#             ordinal = re.findall(r'\d+', file)[0]
#             with open(f'{OUTPUT_DIR}/{file}', 'r') as f:
#                 fib_num = f.read()
#             result.write(f'{ordinal},{fib_num}\n')


def get_one_file_data(file):
    ordinal = re.findall(r'\d+', file)[0]
    with open(f'{OUTPUT_DIR}/{file}', 'r') as f:
        return ordinal, f.read()


def func2(result_file):
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        result = executor.map(get_one_file_data, os.listdir(OUTPUT_DIR))
    with open(result_file, 'w') as f:
        f.write('ordinal,fibonacci\n')
        for vals in result:
            f.write(f'{vals[0]},{vals[1]}\n')


if __name__ == '__main__':
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    array = [randint(1000, 100000) for _ in range(1000)]
    start = perf_counter()
    func1(array=array)
    duration = perf_counter() - start
    print(f'func1 took {duration:.2f} seconds', flush=True)

    start = perf_counter()
    func2(result_file=RESULT_FILE)
    duration = perf_counter() - start
    print(f'func2 took {duration:.2f} seconds', flush=True)
