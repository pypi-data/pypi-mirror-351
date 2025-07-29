import re
from pfylter.core import AbstractFilter, AllFilters, AnyFilter, NotFilter

class LenFilter(AbstractFilter[str]):
        def __init__(self, length: int) -> None:
            self.length = length

        def keep(self, instance: str) -> bool:
            return len(instance) == self.length


class LengthRangeFilter(AbstractFilter[str]):
    def __init__(self, min_len: int, max_len: int) -> None:
        self.min_len = min_len
        self.max_len = max_len

    def keep(self, instance: str) -> bool:
        return self.min_len <= len(instance) <= self.max_len


class StartsWithFilter(AbstractFilter[str]):
    def __init__(self, start: str) -> None:
        self.start = start

    def keep(self, instance: str) -> bool:
        return instance.startswith(self.start)


class EndsWithFilter(AbstractFilter[str]):
    def __init__(self, suffix: str) -> None:
        self.suffix = suffix

    def keep(self, instance: str) -> bool:
        return instance.endswith(self.suffix)


class ContainsFilter(AbstractFilter[str]):
    def __init__(self, substring: str) -> None:
        self.substring = substring

    def keep(self, instance: str) -> bool:
        return self.substring in instance


class RegexFilter(AbstractFilter[str]):
    def __init__(self, pattern: str) -> None:
        self.pattern = re.compile(pattern)

    def keep(self, instance: str) -> bool:
        return bool(self.pattern.search(instance))

if __name__ == '__main__':
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

    print('Strings with length four and starting with "A" or length one and starting with "B":')
    print(AnyFilter([
            AllFilters([LenFilter(4), StartsWithFilter('A')]),
            AllFilters([LenFilter(1), StartsWithFilter('B')])
        ]).apply(example))

    print('Strings starting with "A" and either length one or length four:')
    print(AllFilters([
           StartsWithFilter("A"), 
           AnyFilter([LenFilter(1), LenFilter(4)])
        ]).apply(example))

    print('Exclude any string that includes BC or has length 1 (using AllFilters):')
    print(AllFilters([NotFilter(LenFilter(1)), NotFilter(ContainsFilter('BC'))]).apply(example))

    print('Exclude any string that includes BC or has length 1 (using AnyFilter):')
    print(NotFilter(AnyFilter([ContainsFilter('BC'), LenFilter(1)])).apply(example))

    print('Strings that start with A followed by any chars and ends in D or A:')
    print(RegexFilter('^A.*[D|A]$').apply(example))
