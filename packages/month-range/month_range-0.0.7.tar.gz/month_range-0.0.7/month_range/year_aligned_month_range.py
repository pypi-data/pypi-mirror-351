import math
from abc import ABC
from datetime import date, datetime
from decimal import Decimal
from fractions import Fraction
from functools import total_ordering
from typing import Generic, TypeVar, Literal, Type, Tuple, Any, Mapping, Collection, Sequence

from .month_range import MonthRange
from .parse_util import parse_year_int, unpack_nested

TI = TypeVar("TI", bound=Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
TS = TypeVar("TS", bound="YearAlignedMonthRange")


@total_ordering
class YearAlignedMonthRange(MonthRange, Generic[TI], ABC):
    MONTH_COUNT: Literal[1, 2, 3, 4, 6, 12]
    SERIALIZATION_KEYS: Tuple[str, ...]

    def __init__(self, year: int, index: int) -> None:
        # handle out of range index offsets
        index -= 1
        year_divider = 12 // self.MONTH_COUNT
        year += math.floor(index / year_divider)
        index = index % year_divider
        super().__init__(
            start=MonthRange.__atomic_type__(year=year, index=self.MONTH_COUNT * index + 1),
            end=MonthRange.__atomic_type__(year=year, index=self.MONTH_COUNT * index + self.MONTH_COUNT),
        )

    def __str__(self) -> str:
        return f"{self.year}-{self.SERIALIZATION_KEYS[-1]}{str(self.index).zfill(12 // self.MONTH_COUNT // 10 + 1)}"

    @classmethod
    def parse(cls: Type[TS], v: Any, *, year_align: bool = True) -> TS:
        try:
            if isinstance(v, date | datetime):
                return cls(v.year, math.ceil(v.month / cls.MONTH_COUNT))
            elif isinstance(v, str):
                # this method is overridden in Year. No need to take care of that case here
                parts = v.split("-")
                if len(parts) == 2:
                    return cls(parse_year_int(parts[0]), cls._parse_index(parts[1]))
            elif isinstance(v, Mapping):
                return cls(parse_year_int(v), cls._parse_index(v))
            elif isinstance(v, Sequence) and len(v) == 2:
                return cls(parse_year_int(v[0]), cls._parse_index(v[1]))
        except Exception:
            pass
        cls._abort_parse(v)

    @classmethod
    def _parse_index(cls, v: Any) -> TI:
        original_v = v
        v = unpack_nested(v, cls.SERIALIZATION_KEYS)
        if isinstance(v, int) and 0 < v <= 12 // cls.MONTH_COUNT:
            return v  # type: ignore

        if isinstance(v, str):
            v = v.lower().strip()
            for key in cls.SERIALIZATION_KEYS:
                if v.startswith(key):
                    v = v[len(key) :].strip()
                    if v.isdigit():
                        return cls._parse_index(int(v))

        elif isinstance(v, float | Decimal | Fraction):
            return cls._parse_index(int(math.floor(v)))

        elif isinstance(v, Mapping):
            for key in v.keys():
                if key.lower() in cls.SERIALIZATION_KEYS:
                    return cls._parse_index(v[key])

        elif isinstance(v, Collection) and len(v) == 1:
            return cls._parse_index(next(iter(v)))

        raise ValueError(f"unable to parse {original_v} as {cls.__name__} index")

    @property
    def year(self) -> int:
        return self.first_month.year

    @property
    def index(self) -> TI:
        return math.ceil(self.first_month.index / self.MONTH_COUNT)  # type: ignore

    @classmethod
    def current(cls: Type[TS]) -> TS:
        today = date.today()
        return cls(year=today.year, index=math.ceil(today.month / cls.MONTH_COUNT))

    # the following methods are redefined here for performance reasons
    @property
    def month_count(self) -> int:
        return self.MONTH_COUNT

    def year_align(self: TS) -> TS:
        return self

    def next(self: TS, offset: int = 1) -> TS:
        return self.__class__(year=self.year, index=self.index + offset)  # type: ignore

    def prev(self: TS, offset: int = 1) -> TS:
        return self.__class__(year=self.year, index=self.index - offset)  # type: ignore
