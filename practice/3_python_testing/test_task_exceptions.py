"""
Write tests for division() function in 2_python_part_2/task_exceptions.py
In case (1,1) it should check if exception were raised
In case (1,0) it should check if return value is None and "Division by 0" printed
If other cases it should check if division is correct

TIP: to test output of print() function use capfd fixture
https://stackoverflow.com/a/20507769
"""

import sys
import os
import pytest

FOLDER = '2_python_part_2'
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), FOLDER))


class TestExceptions:
    import task_exceptions as task_ex

    def test_division_ok(self, capfd):
        d = self.task_ex.division(15, 3)
        out, err = capfd.readouterr()
        assert d == 5
        assert 'Division finished' in out

        d = self.task_ex.division(-20, 10)
        out, err = capfd.readouterr()
        assert d == -2
        assert 'Division finished' in out

        d = self.task_ex.division(100, -4)
        out, err = capfd.readouterr()
        assert d == -25
        assert 'Division finished' in out

    def test_division_by_zero(self, capfd):
        with pytest.raises(ZeroDivisionError):
            d = self.task_ex.division(100, 0)
            out, err = capfd.readouterr()
            assert d is None
            assert 'Division by 0' in err
            assert 'Division finished' in out

    def test_division_by_one(self, capfd):
        with pytest.raises(self.task_ex.DivisionByOneException):
            d = self.task_ex.division(50, 1)
            out, err = capfd.readouterr()
            assert d == 50
            assert 'Division by 1 gets the same result' in err
            assert 'Division finished' in out
