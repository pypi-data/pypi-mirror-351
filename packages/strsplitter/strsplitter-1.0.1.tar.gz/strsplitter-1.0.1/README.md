# strsplit

A flexible string splitting utility for Python that allows splitting by different strategies and filtering the results using predicates.
This package is inspired by the abseil StrSplit library.

![PyPI](https://img.shields.io/pypi/v/strsplit)
![Python Version](https://img.shields.io/pypi/pyversions/strsplit)
[![Supported Versions](https://img.shields.io/pypi/pyversions/requests.svg)]

## Features

- Split by a delimiter string (`SplitByStr`)
- Split by fixed length chunks (`SplitByLength`)
- Split by any character in a set (`SplitByAnyChar`)
- Control maximum splits with `maxsplit` parameter (default `-1` = no limit)
- Filter out substrings via a predicate function in the main `split` function

## Usage

```python
from strsplit import split, SplitByStr, SplitByAnyChar, SplitByLength
# Split using a string delimiter
it = split(text="a,b,c", ",") # <=> it = split(text="a,b,c", splitter=SplitByStr(","))
print(list(it)) # --> ['a', 'b', 'c']

# Split by any chars
it = split(text="a,b;c-d", [",", ";", "-"]) # <=> it = split(text="a,b,c", splitter=SplitByAnChar(",;-"))
print(list(it)) # --> ['a', 'b', 'c', 'd']

# Split by length
it = split(text="abcdef", splitter=SplitByLength(2)) # <=> it = split(text="abcdef", 2)
print(list(it)) # --> ["ab", "cd", "ef"]

# Use a predicat to filter the result 
it = split(",a,,b,c,", ",", lambda x : len(x) > 0)
print(list(it)) # --> ['a', 'b', 'c']

# Limit the number of substr
# Every splitter accepts another parameter maxsplit to limit the number of splits
it = split(text="a,b,c,d", SplitByStr(delimiter=",", maxsplit=2))
print(list(it)) # --> ['a', 'b']
```
