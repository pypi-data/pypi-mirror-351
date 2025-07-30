from typing import Any

import pytest
from click.testing import CliRunner

from strsplitter import SplitByAnyChar, SplitByLength, SplitByStr, split
from strsplitter.__main__ import main


def always_false(_: str) -> bool:
    return False


def always_true(_: str) -> bool:
    return True


@pytest.mark.split_api
class TestSplitApi:
    text = 'a,b,c'

    def test_splitter_param_str(self):
        it = split(self.text, ',')
        assert list(it) == ['a', 'b', 'c']

    def test_splitter_param_tuple(self):
        it = split(self.text, (',', 3))
        assert list(it) == ['a', 'b', 'c']

    def test_splitter_param_list(self):
        it = split('a,b;c', [',', ';'])
        assert list(it) == ['a', 'b', 'c']

    def test_splitter_param_int(self):
        it = split(self.text, 2)
        assert list(it) == ['a,', 'b,', 'c']

    def test_splitter_param_none(self):
        _text = 'a b\nc'
        it = split(_text)
        assert list(it) == ['a', 'b', 'c']

    def test_splitter_wrong_params(self):
        with pytest.raises(TypeError):
            split(self.text, 2.4)


@pytest.mark.split_by_str
class TestSplitByStr:
    str_splitter = SplitByStr(delimiter=',')

    def test_split_by_str_stop_iteration(self):
        text = 'a,b,c'
        it = split(text, self.str_splitter)
        next(it)  # 'a'
        next(it)  # 'b'
        next(it)  # 'c'
        # After consuming all elements, StopIteration should be raised.
        with pytest.raises(StopIteration):  # type: ignore
            next(it)

    def test_split_by_str_basic(self):
        text = 'a,b,c'
        it = split(text, self.str_splitter)
        assert iter(it) is it
        assert next(it) == 'a'
        assert next(it) == 'b'
        assert next(it) == 'c'

    def test_split_by_str_with_long_delimiter(self):
        text = 'I knowthatyou knowthatI know.'
        it = split(text, SplitByStr('that'))
        assert list(it) == ['I know', 'you know', 'I know.']

    def test_split_by_str_empty_string(self):
        # Empty string should yield an empty iterator.
        text = ''
        it = split(text, self.str_splitter)  # type: ignore
        assert list(it) == ['']

    def test_split_by_str_trailing_delimiters(self):
        # Leading and trailing empty substrings.
        it = split(',a,b,c,', self.str_splitter)
        assert list(it) == ['', 'a', 'b', 'c', '']

    def test_split_by_str_multiple_consecutive_delimiters(self):
        # Multiple consecutive delimiters should yield empty substrings.
        it = split('a,,b,c', self.str_splitter)
        assert list(it) == ['a', '', 'b', 'c']

    def test_split_by_str_delimiter_not_found(self):
        text = 'a,b,c,d'
        result = split(text, SplitByStr('-'))
        assert list(result) == ['a,b,c,d']


@pytest.mark.split_by_length
class TestSplitByLength:
    def test_split_by_length_stop_iteration(self):
        text = 'abcd'
        it = split(text, SplitByLength(2))
        next(it)  # 'ab'
        next(it)  # 'cd'
        # After consuming all elements, StopIteration should be raised.
        with pytest.raises(StopIteration):  # type: ignore
            next(it)

    def test_split_by_length_basic(self):
        text = 'abcdef'
        it = split(text, SplitByLength(3))
        assert iter(it) is it
        assert next(it) == 'abc'
        assert next(it) == 'def'

    def test_split_by_length_odd(self):
        text = 'abcdefg'
        it = split(text, SplitByLength(3))
        assert list(it) == ['abc', 'def', 'g']

    def test_split_by_length_even(self):
        text = 'abcdef'
        it = split(text, SplitByLength(2))
        assert list(it) == ['ab', 'cd', 'ef']

    def test_split_by_length_bigger_then_text(self):
        text = 'ab'
        it = split(text, SplitByLength(4))
        assert list(it) == ['ab']

    def test_split_by_length_of_one(self):
        text = 'abc'
        it = split(text, SplitByLength(1))
        assert list(it) == ['a', 'b', 'c']


@pytest.mark.by_any_char
class TestSplitByAnyChar:
    def test_split_by_any_char_basic(self):
        text = 'a,b;c-d'
        it = split(text, SplitByAnyChar(',;-'))
        assert iter(it) is it
        assert next(it) == 'a'
        assert next(it) == 'b'
        assert next(it) == 'c'
        assert next(it) == 'd'
        with pytest.raises(StopIteration):
            next(it)

    def test_split_by_any_chars_consecutive_delimiters(self):
        text = ',a;:b '
        it = split(text, SplitByAnyChar(' ,:;'))
        assert list(it) == ['', 'a', '', 'b', '']

    def test_split_by_any_char_not_found_delimiters(self):
        text = 'a,b,c'
        it = split(text, SplitByAnyChar(' :;'))
        assert list(it) == ['a,b,c']


@pytest.mark.split_with_predicat
def test_split_with_predicat():
    text = '1,2,3,4,5,6'
    it = split(text, ',', lambda x: int(x) > 3)
    assert list(it) == ['4', '5', '6']


@pytest.mark.split_with_predicat
def test_split_with_predicate_always_true():
    text = '1,2,3,4'
    it = split(text, ',', always_true)
    assert list(it) == ['1', '2', '3', '4']


@pytest.mark.split_with_predicat
def test_split_with_predicate_always_false():
    text = '1,2,3,4'
    it = split(text, ',', always_false)
    assert list(it) == []


@pytest.mark.split_with_predicat
def test_split_with_predicate_skip_empty_substr():
    text = ',1,,2,'
    it = split(text, ',', lambda x: len(x) > 0)
    assert list(it) == ['1', '2']


@pytest.mark.split_with_maxsplit
def test_split_given_max_split():
    text = '1,2,3,4,5,6'
    it = split(text, (',', 3))
    assert list(it) == ['1', '2', '3']


@pytest.mark.split_with_maxsplit
def test_split_given_max_split_zero_length():
    text = '1,2,3,4,5,6'
    it = split(text, (',', 0))
    assert list(it) == []


@pytest.mark.split_cli
def test_split_cli(tmp_path: Any):
    test_file = tmp_path / 'input.txt'
    test_file.write_text('a,b;c')

    runner = CliRunner()
    result = runner.invoke(main, ['--delimiters', ',;'] + [str(test_file)])
    assert result.exit_code == 0
    assert result.output.strip() == 'a\nb\nc'


@pytest.mark.split_cli
def test_split_cli_file_not_found():
    test_file = 'non_existent_file.txt'
    runner = CliRunner()
    result = runner.invoke(main, ['--delimiters', ',;'] + [test_file])

    assert result.exit_code != 0
    assert "Error: File 'non_existent_file.txt' not found." in result.output


@pytest.mark.split_cli
def test_split_cli_no_delimiters(tmp_path: Any):
    test_file = tmp_path / 'input.txt'
    test_file.write_text('a b\nc')

    runner = CliRunner()
    result = runner.invoke(main, [str(test_file)])

    assert result.exit_code == 0
    assert result.output.strip() == 'a\nb\nc'
