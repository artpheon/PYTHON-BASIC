"""
Write function which executes custom operation from math module
for given arguments.
Restrition: math function could take 1 or 2 arguments
If given operation does not exists, raise OperationNotFoundException
Examples:
     >>> math_calculate('log', 1024, 2)
     10.0
     >>> math_calculate('ceil', 10.7)
     11
"""
import math
import pytest


class OperationNotFoundException(Exception):
    pass


def math_calculate(function: str, *args):
    try:
        method_to_call = getattr(math, function)
    except AttributeError as exc:
        raise OperationNotFoundException from exc
    else:
        return method_to_call(*args)


"""
Write tests for math_calculate function
"""


class TestMathCalculate:
    OP_1 = 'isinf'
    OP_2 = 'pow'
    OP_3 = 'sqrt'
    OP_4 = 'log10'
    WRONG_OP_1 = 'wrong_op'
    WRONG_OP_2 = 'logs'
    TEST_OPERATIONS = [
        ([OP_1, math.inf], True),
        ([OP_1, 99], False),
        ([OP_2, 2, 5], 32),
        ([OP_2, 10, 5], 100000),
        ([OP_3, 49], 7),
        ([OP_3, 144], 12),
        ([OP_4, 100], 2.0),
        ([OP_4, 100000], 5.0),
    ]
    TEST_WRONG_OPERATIONS = [
        ([WRONG_OP_1, 42], pytest.raises(OperationNotFoundException)),
        ([WRONG_OP_2, 666], pytest.raises(OperationNotFoundException)),
    ]

    @pytest.mark.parametrize('test_input,expected', TEST_OPERATIONS)
    def test_operations(self, test_input, expected):
        """Tests correct operations with the correct arguments"""
        assert math_calculate(*test_input) == expected

    @pytest.mark.parametrize('test_input,expectation', TEST_WRONG_OPERATIONS)
    def test_wrong_operations(self, test_input, expectation):
        """Tests that wrong, non-existing operations raise exception"""
        with expectation:
            assert math_calculate(*test_input) is not None

    def test_incorrect_args(self):
        """Tests that operations with wrong input arguments raise exceptions"""
        with pytest.raises(Exception):
            assert math_calculate(self.OP_1, 12, 23, 34, 0, 200)
        with pytest.raises(Exception):
            assert math_calculate(self.OP_2)
