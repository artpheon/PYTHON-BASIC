"""
Write a parametrized test for two functions.
The functions are used to find a number by ordinal in the Fibonacci sequence.
One of them has a bug.

Fibonacci sequence: https://en.wikipedia.org/wiki/Fibonacci_number

Task:
 1. Write a test with @pytest.mark.parametrize decorator.
 2. Find the buggy function and fix it.
"""
import pytest


def fibonacci_1(n):
    a, b = 0, 1
    # added checking for n == 0
    if n == 0:
        return a
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def fibonacci_2(n):
    fibo = [0, 1]
    for i in range(1, n + 1):
        # this was wrong: fibo.append(fibo[i - 1] + fibo[i - 2])
        fibo.append(fibo[i] + fibo[i - 1])
    return fibo[n]


# 0 1 1 2 3 5 8 13 21 34 55 89
TEST_SEQUENCE = [(0, 0),
                 (1, 1),
                 (2, 1),
                 (3, 2),
                 (9, 34)]


@pytest.mark.parametrize('test_input,expected', TEST_SEQUENCE)
def test_fib_1(test_input, expected):
    assert fibonacci_1(test_input) == expected


@pytest.mark.parametrize('test_input,expected', TEST_SEQUENCE)
def test_fib_2(test_input, expected):
    assert fibonacci_2(test_input) == expected
