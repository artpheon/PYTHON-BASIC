"""
Write function which receives filename and reads file line by line and returns min and mix integer from file.
Restriction: filename always valid, each line of file contains valid integer value
Examples:
    # file contains following lines:
        10
        -2
        0
        34
    >>> get_min_max('filename')
    (-2, 34)

Hint:
To read file line-by-line you can use this:
with open(filename) as opened_file:
    for line in opened_file:
        ...
"""
from typing import Tuple


def get_min_max(filename: str) -> Tuple[int, int]:
    """Reads a file filename and gets the biggest and the smallest integer."""
    with open(filename, 'r') as f:
        min_int, max_int = float('+inf'), float('-inf')
        for num in f.readlines():
            min_int, max_int = min(int(num), min_int), max(int(num), max_int)
        return min_int, max_int
