from __future__ import annotations

import math
from datetime import date
from typing import Any, Literal, Type, List, Tuple

from ..year_aligned_month_range import YearAlignedMonthRange


class Month(YearAlignedMonthRange[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]):
    MONTH_COUNT: Literal[1] = 1
    SERIALIZATION_KEYS: Tuple[str, ...] = "month", "month", "mon", "m", ""

    _year: int
    _index: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    # noinspection PyMissingConstructor
    def __init__(self, year: int, index: int) -> None:
        index = index - 1
        self._year = year + math.floor(index / 12)
        self._index = (index % 12) + 1  # type: ignore
        self._first_month = self
        self._last_month = self

    @classmethod
    def parse(cls, v: Any, *, year_align: bool = True) -> Month:
        original_v = v
        # handle YYYYMM format
        if isinstance(v, str):
            v = v.strip()
            if v.isdigit():
                v = int(v)
        if isinstance(v, int):
            if 100001 <= v <= 999912:
                index = v % 100
                if 1 <= index <= 12:
                    return cls(v // 100, index)
        return super().parse(original_v, year_align=year_align)  # type: ignore

    # the following methods rely on first_month in superclasses and have to be redefined here to avoid infinite recursion
    @property
    def year(self) -> int:
        return self._year

    @property
    def index(self) -> Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
        return self._index

    # the following methods are redefined here for performance reasons
    @classmethod
    def current(cls) -> Month:
        today = date.today()
        return cls(today.year, today.month)

    def next(self, offset: int = 1) -> Month:
        return Month(year=self.year, index=self.index + offset)

    def prev(self, offset: int = 1) -> Month:
        return Month(year=self.year, index=self.index - offset)

    def split(self, by: Type[YearAlignedMonthRange] = None, year_align: bool = True) -> List[Month]:
        return [self]
