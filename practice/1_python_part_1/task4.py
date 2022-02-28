"""
Write function which receives list of integers. Calculate power of each integer and
subtract difference between original previous value and it's power. For first value subtract nothing.
Restriction:
Examples:
    >>> calculate_power_with_difference([1, 2, 3])
    [1, 4, 7]  # because [1^2, 2^2 - (1^2 - 1), 3^2 - (2^2 - 2)]
"""
from typing import List


def calculate_power_with_difference(ints: List[int]) -> List[int]:
    """Returns a list with values being raised to power 2 and calculated differences."""
    power = 2
    result = list()
    for ind, val in enumerate(ints):
        if ind == 0:
            result.append(val ** power)
        else:
            result.append(val ** power - (ints[ind-1] ** power - ints[ind-1]))
    # the same, but with listcomp (less readable):
    # result = [val ** power if ind == 0 else val ** power - (ints[ind-1] ** power - ints[ind-1])
    #          for ind, val in enumerate(ints)]
    return result
