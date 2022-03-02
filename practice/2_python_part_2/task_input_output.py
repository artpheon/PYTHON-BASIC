"""
Write function which reads a number from input nth times.
If an entered value isn't a number, ignore it.
After all inputs are entered, calculate an average entered number.
Return string with following format:
If average exists, return: "Avg: X", where X is avg value which rounded to 2 places after the decimal
If it doesn't exists, return: "No numbers entered"
Examples:
    user enters: 1, 2, hello, 2, world
    >>> read_numbers(5)
    Avg: 1.67
    ------------
    user enters: hello, world, foo, bar, baz
    >>> read_numbers(5)
    No numbers entered

"""


def read_numbers(n: int) -> str:
    """Read integer n times from user input, and return a string displaying the average number."""
    num = 0
    count = 0
    for _ in range(n):
        try:
            num = num + int(input())
        except ValueError:
            num = num + 0
        else:
            count = count + 1
    try:
        return f'Avg: {num / count:.2f}'
    except ZeroDivisionError:
        return 'No numbers entered'
