from collections.abc import Callable, Iterator
from typing import Any

from .iterator import make_iterator
from .splitter import SplitByAnyChar, SplitByLength, SplitByStr, Splitter


def split(
    text: str, splitter: Any = None, predicate: Callable[[str], bool] | None = None
) -> Iterator[str]:
    """Split a string using the specified splitter.

    Parameters:
    -----------
    text : str
        The string to split.
    splitter : Splitter, str, list[str], None
        An instance of Splitter or a string/tuple defining the splitter.
        Setting this parameter to None will split on any whitespace character.
    :predicate : Callable
        Optional predicate function to filter the results.

    Returns:
    --------
    Iterator[str]
        An iterator yielding the split substrings.

    Raises:
    -------
    TypeError
        If the splitter is not of a valid type.

    Examples:
    ---------
    >>> from strsplitter import split
    >>> text = 'Hello, world! This is a test.'
    >>> for part in split(text, ','):
    ...     print(part)
    Hello
     world! This is a test.
    >>> for part in split(text, (' ', 2)):
    ...     print(part)
    Hello,
    world! This is a test.
    >>> skip_empty = lambda x: x != ''
    >>> for part in split(text, [' ', ','], skip_empty):
    ...     print(part)
    Hello
    world!
    This
    is
    a
    test
    """

    _splitter = None
    match splitter:
        case int():
            _splitter = SplitByLength(splitter)
        case str():
            _splitter = SplitByStr(splitter)
        case (_s, _num) if isinstance(_s, str) and isinstance(_num, int):
            _splitter = SplitByStr(delimiter=_s, maxsplit=_num)
        case list() if all(isinstance(i, str) for i in splitter):  # type: ignore
            _splitter = SplitByAnyChar(chars=''.join(splitter))  # type: ignore
        case None:
            _splitter = SplitByAnyChar(' \n\r\t\f')
        case Splitter():
            _splitter = splitter
        case _:
            raise TypeError(
                'splitter must be a Splitter instance,str, list[str] or tuple[str, int]'
            )
    return make_iterator(_splitter, text, predicate)
