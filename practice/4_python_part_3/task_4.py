"""
Create virtual environment and install Faker package only for this venv.
Write command line tool which will receive int as a first argument and one or more named arguments
 and generates defined number of dicts separated by new line.
Exec format:
`$python task_4.py NUMBER --FIELD=PROVIDER [--FIELD=PROVIDER...]`
where:
NUMBER - positive number of generated instances
FIELD - key used in generated dict
PROVIDER - name of Faker provider
Example:
`$python task_4.py 2 --fake-address=address --some_name=name`
{"some_name": "Chad Baird", "fake-address": "62323 Hobbs Green\nMaryshire, WY 48636"}
{"some_name": "Courtney Duncan", "fake-address": "8107 Nicole Orchard Suite 762\nJosephchester, WI 05981"}
"""

import argparse
import unittest
from faker import Faker
from unittest.mock import Mock


def print_name_address(parser: argparse.Namespace) -> None:
    fake = Faker()
    fake_data = []
    for n in range(parser.num):
        data = dict()
        value = None
        for i in parser.values:
            arg = i.split('=')
            try:
                value = getattr(fake, arg[1])()
            except AttributeError:
                # if faker cannot provide a specific method,
                # we ask to create a short random text
                value = fake.sentence(nb_words=3)
            except IndexError:
                raise SyntaxError(f'argument {arg} has incorrect syntax') from None
            finally:
                data[arg[0]] = value
        fake_data.append(data)
    for data in fake_data:
        print(data)


class FieldProviderError(Exception):
    pass


class KeyValGenerator:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description='Get key=value pairs')
        self.parser.add_argument('num', metavar='NUMBER', type=int, default=0)
        self.parser.add_argument('values', metavar='FIELD=PROVIDER', nargs='+')

    def get_parser(self) -> argparse.Namespace:
        return self.parser.parse_args()


if __name__ == '__main__':
    g = KeyValGenerator()
    print_name_address(g.get_parser())

"""
Write test for print_name_address function
Use Mock for mocking args argument https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock
Example:
    >>> m = Mock()
    >>> m.method.return_value = 123
    >>> m.method()
    123
"""


class TestFieldProvider(unittest.TestCase):
    NUM = str(4)
    FIELD_1 = 'fake_name'
    FIELD_2 = 'fake_address'
    PROVIDER_1 = 'name'
    PROVIDER_2 = 'address'
    args = [NUM, f'{FIELD_1}={PROVIDER_1}', f'{FIELD_2}={PROVIDER_2}']

    def test_cli_arguments(self):
        m = Mock()
        m.print_name_address(self.args)
        m.print_name_address.assert_called_with(self.args)
