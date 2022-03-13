"""
using datetime module find number of days from custom date to now
Custom date is a string with format "2021-12-24"
If entered string pattern does not match, raise a custom Exception
If entered date is from future, return negative value for number of days
    >>> calculate_days('2021-10-07')  # for this example today is 6 october 2021
    -1
    >>> calculate_days('2021-10-05')
    1
    >>> calculate_days('10-07-2021')
    WrongFormatException
"""
from datetime import datetime, date
import pytest


class WrongFormatException(Exception):
    pass


def calculate_days(from_date: str) -> int:
    try:
        calculated = datetime(*[int(i) for i in from_date.split('-')])
    except Exception as exc:
        raise WrongFormatException('Wrong format for data. Tip: YYYY-MM-DD') from exc
    else:
        return datetime.now().day - calculated.day


"""
Write tests for calculate_days function
Note that all tests should pass regardless of the day test was run
Tip: for mocking datetime.now() use https://pypi.org/project/pytest-freezegun/
"""


class TestTime:
    @pytest.fixture
    def current_date(self):
        return date.today()

    @pytest.mark.freeze_time
    def test_date_positive(self, current_date, freezer):
        freezer.move_to('2019-01-23')
        assert calculate_days('2019-01-20') == 3

    @pytest.mark.freeze_time
    def test_date_negative(self, current_date, freezer):
        freezer.move_to('2022-03-10')
        assert calculate_days('2022-03-15') == -5

    @pytest.mark.freeze_time
    def test_date_same(self, current_date, freezer):
        freezer.move_to('2010-10-10')
        assert calculate_days('2010-10-10') == 0

    def test_date_wrong_format(self, current_date):
        with pytest.raises(WrongFormatException):
            assert calculate_days('2012/12/12') is not None
        with pytest.raises(WrongFormatException):
            assert calculate_days('2012-22-22') is not None
        with pytest.raises(WrongFormatException):
            assert calculate_days('29-04-1997') is not None
