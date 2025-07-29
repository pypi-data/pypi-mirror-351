# 🔍 pfylter [![PyPI](https://img.shields.io/pypi/v/pfylter.svg?logo=pypi&label=PyPI)](https://pypi.org/project/pfylter/) [![GitHub](https://img.shields.io/badge/GitHub-hlfernandez%2Fpfylter-blue?logo=github)](https://github.com/hlfernandez/pfylter)

**pfylter** is a lightweight, flexible, and extensible Python framework for applying composable filters to arbitrary data. It’s built using the **composite design pattern**, allowing complex logical conditions to be expressed and reused cleanly.

---

## 📑 Table of Contents

- [🔍 pfylter  ](#-pfylter--)
  - [📑 Table of Contents](#-table-of-contents)
  - [🚀 Features](#-features)
  - [📦 Installation](#-installation)
  - [✨ Quick Start](#-quick-start)
  - [🧩 Predefined String Filters](#-predefined-string-filters)
  - [🛠 Creating Custom Filters](#-creating-custom-filters)
  - [📝 License](#-license)
  - [🤝 Contributing](#-contributing)

---

## 🚀 Features

- ✅ Define your own filters by subclassing `AbstractFilter`
- ✅ Combine filters using logical **AND** (`AllFilters`) or **OR** (`AnyFilter`)
- ✅ Support for generic data types (strings, numbers, objects, etc.)
- ✅ Clean, readable syntax using list comprehensions and type hints
- ✅ Perfect for data processing, rule engines, and validation pipelines

---

## 📦 Installation

```bash
pip install pfylter
```

---

## ✨ Quick Start

These simple examples with number uses the `LambdaFilter` class to build filters based on lambda functions.

Let's start with a simple filter to get numbers greater than 5 or it's oposite condition using `NotFilter`.

```python
from pfylter.core import LambdaFilter, NotFilter, AllFilters, AnyFilter

example = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

print('Numbers greater than 5:')
print(LambdaFilter(lambda x: x > 5).apply(example))  # [6, 7, 8, 9, 10]

print('Numbers equal or lower than 5:')
print(NotFilter(LambdaFilter(lambda x: x > 5)).apply(example))  # [1, 2, 3, 4, 5]
```

Now, use `AllFilters` and `AnyFilter` to create filters by aggregating other filters. When `AllFilters` is used, only elements that meet all filters in the list are kept.

```python

print('Numbers greater than 5 and divisible by two:')
print(AllFilters([
    LambdaFilter(lambda x: x > 5),
    LambdaFilter(lambda x: x % 2 == 0)
]).apply(example))  # [6, 8, 10]

print('Numbers greater than 5 and divisible by three:')
print(AllFilters([
    LambdaFilter(lambda x: x > 5),
    LambdaFilter(lambda x: x % 3 == 0)
]).apply(example))  # [6, 9]

```
 
 When `AnyFilter`, elements that meet any of the filters in the list are kept (i.e. meet any of the filters is enough to be in the output).

```python
print('Numbers greater than 5 or divisible by two:')
print(AnyFilter([
    LambdaFilter(lambda x: x > 5),
    LambdaFilter(lambda x: x % 2 == 0)
]).apply(example))  # [2, 4, 6, 7, 8, 9, 10]
```

---

## 🧩 Predefined String Filters

The `pfylter.strings` module provides ready-to-use filters for common string operations:

- `LenFilter(length)`: keeps strings of a given length.
- `LengthRangeFilter(min, max)`: keeps strings of length within the specified range.
- `EndsWithFilter(prefix)`: keeps strings that start with a prefix.
- `StartsWithFilter(prefix)`: keeps strings that end with a prefix.
- `ContainsFilter(substring)`: keeps strings that contain a substring.
- `RegexFilter(substring)`: keeps strings that match the specified regular expression.

Starting with a list of strings, here we have some uses of these basic filters.
```python
from pfylter.strings import LenFilter, StartsWithFilter, ContainsFilter, NotFilter
from pfylter.core import AllFilters, AnyFilter

example = ['A', 'ABCD', 'B', 'BCDE', 'C', 'AAAAAAA']

print('Strings containing "BC":')
print(ContainsFilter('BC').apply(example))

print('Strings with length one:')
print(LenFilter(1).apply(example))

print('Strings with length different than one:')
print(NotFilter(LenFilter(1)).apply(example))

print('Strings with length four and starting with "A":')
print(AllFilters([LenFilter(4), StartsWithFilter('A')]).apply(example))  

print('Strings with length four or starting with "A":')
print(AnyFilter([LenFilter(4), StartsWithFilter('A')]).apply(example))
```

More complex filters can be created creating an `AnyFilter` with two `AllFilters` objects to output all strings that either have length four and start with "A" or have length one and start with "B".

```python
print('Strings with length four and starting with "A" or length one and starting with "B":')
print(AnyFilter([
    AllFilters([LenFilter(4), StartsWithFilter('A')]),
    AllFilters([LenFilter(1), StartsWithFilter('B')])
]).apply(example))  # ['ABCD', 'B']
```

Finally, the `NotFilter` can be combined with `AllFilters` or `AnyFilter` to create exclusion filters. These two examples are equivalent and allow excluding strings that contain "BC" (this excludes "ABCD" and "BCDE") or have length 1 (this excludes "A", "B, and "C").

```python
print('Exclude any string that includes BC or has length 1 (using AllFilters):')
print(AllFilters([NotFilter(LenFilter(1)), NotFilter(ContainsFilter('BC'))]).apply(example))  # ['AAAAAAA']

print('Exclude any string that includes BC or has length 1 (using AnyFilter):')
print(NotFilter(AnyFilter([ContainsFilter('BC'), LenFilter(1)])).apply(example))  # ['AAAAAAA']
```

---

## 🛠 Creating Custom Filters

You can define custom filters by inheriting from `AbstractFilter`:

```python
from pfylter import AbstractFilter

class GreaterThanFilter(AbstractFilter[int]):
    def __init__(self, threshold: int):
        self.threshold = threshold

    def keep(self, instance: int) -> bool:
        return instance > self.threshold
```

Now you can use this filter in combination with others!

---

## 📝 License

MIT License — see `LICENSE` file for details.

---

## 🤝 Contributing

Feel free to open issues or pull requests. All feedback is welcome!
