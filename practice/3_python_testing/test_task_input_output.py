"""
Write tests for a read_numbers function.
It should check successful and failed cases
for example:
Test if user inputs: 1, 2, 3, 4
Test if user inputs: 1, 2, Text

Tip: for passing custom values to the input() function
Use unittest.mock patch function
https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch

TIP: for testing builtin input() function create another function which return input() and mock returned value
"""
import unittest
from unittest.mock import patch
import sys
import os

FOLDER = '2_python_part_2'
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), FOLDER))


without_text = (val for val in [1, 3, 5, 7, 9])
with_text = (val for val in [2, 4, 'some', 8, 'text'])
with_no_int = (val for val in ['here', 'are', 'no', 'numbers', 'at all'])


def mock_input_1():
    return next(without_text)


def mock_input_2():
    return next(with_text)


def mock_input_3():
    return next(with_no_int)


class TestInputOutput(unittest.TestCase):
    import task_input_output as task_io

    @patch('builtins.input', mock_input_1)
    def test_read_numbers_without_text_input(self):
        value = self.task_io.read_numbers(5)
        assert value == 'Avg: 5.00'

    @patch('builtins.input', mock_input_2)
    def test_read_numbers_with_text_input(self):
        value = self.task_io.read_numbers(5)
        assert value == 'Avg: 4.67'

    @patch('builtins.input', mock_input_3)
    def test_read_numbers_with_no_int(self):
        value = self.task_io.read_numbers(5)
        assert value == 'No numbers entered'


if __name__ == '__main__':
    unittest.main(verbosity=2)
