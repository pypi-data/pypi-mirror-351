import itertools
from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")


def pairwise(iterable: Iterable[T]) -> Iterator[tuple[T, T]]:
    # Copied from Python 3.10
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def get_intervals(values: list[int]) -> list[int]:
    """Get all the intervals between numbers.

    It's similar to numpy.diff function.

    Example:
    -------
    >>> get_intervals([1, 4, 5, 6, 10])
    [3, 1, 1, 4]

    """
    all_diffs = []
    for value, next_value in pairwise(values):
        all_diffs.append(next_value - value)
    return all_diffs
