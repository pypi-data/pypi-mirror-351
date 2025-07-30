import abc
from typing import Tuple


class Splitter(abc.ABC):
	@abc.abstractmethod
	def __init__(self, maxsplit: int = -1):
		self._maxsplit = maxsplit

	@property
	def maxsplit(self) -> int:
		"""Maximum number of splits to perform. -1 means no limit."""
		return self._maxsplit

	@maxsplit.setter
	def maxsplit(self, value: int) -> None:
		self._maxsplit = value

	@abc.abstractmethod
	def find(self, text: str, index: int) -> Tuple[int, int]:
		pass


class SplitByStr(Splitter):
	def __init__(self, delimiter: str, maxsplit: int = -1):
		super().__init__(maxsplit)
		if delimiter == '':
			raise ValueError('Delimiter must be a non-empty string')
		self._delim = delimiter

	def find(self, text: str, index: int) -> Tuple[int, int]:
		result: int = text.find(self._delim, index)
		if result == -1:
			result = len(text)
		return result, result + len(self._delim)


class SplitByLength(Splitter):
	def __init__(self, length: int, maxsplit: int = -1):
		super().__init__(maxsplit)
		self._length = length

	def find(self, text: str, index: int) -> Tuple[int, int]:
		if index + self._length >= len(text):
			return len(text), len(text) + 1
		return index + self._length, index + self._length


class SplitByAnyChar(Splitter):
	def __init__(self, chars: str, maxsplit: int = -1):
		super().__init__(maxsplit)
		self._chars = set(chars)

	def find(self, text: str, index: int) -> Tuple[int, int]:
		while index < len(text) and text[index] not in self._chars:
			index += 1
		if index == len(text):
			return index, index + 1
		return index, index + 1
