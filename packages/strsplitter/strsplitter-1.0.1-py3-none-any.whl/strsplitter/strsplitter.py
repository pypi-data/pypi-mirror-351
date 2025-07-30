from typing import Callable, Optional, Any, Iterator
from .splitter import Splitter, SplitByStr, SplitByAnyChar, SplitByLength
from .iterator import make_iterator


def split(
	text: str, splitter: Any = None, predicate: Optional[Callable[[str], bool]] = None
) -> Iterator[str]:
	"""
	Split a string using the specified splitter.
	:param text: The string to split.
	:param splitter: An instance of Splitter or a string/tuple defining the splitter.
	 Setting this parameter to None
	 will split on any whitespace character.
	:param predicate: Optional predicate function to filter the results.
	:return: An iterator yielding the split substrings.
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
			raise TypeError('splitter must be a Splitter instance, str, or tuple')
	return make_iterator(_splitter, text, predicate)
