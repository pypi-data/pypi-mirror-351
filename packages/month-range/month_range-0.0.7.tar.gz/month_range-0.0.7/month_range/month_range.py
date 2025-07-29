from __future__ import annotations

import math
from calendar import monthrange
from datetime import date, datetime
from operator import methodcaller
from typing import TYPE_CHECKING, List, Any, Mapping, Tuple, Type, Sequence, Never, TypeVar
from zoneinfo import ZoneInfo


if TYPE_CHECKING:
    from .year_aligned_month_range import YearAlignedMonthRange
    from .year_aligned import Month

TIMEZONE_NAME = datetime.now().astimezone().tzname()

TS = TypeVar("TS", bound="MonthRange")


class MonthRange:
    # circular deps. those are resolved in the __init__.py
    __atomic_type__: Type[Month]
    __year_aligned_types__: Tuple[Type[YearAlignedMonthRange], ...]

    _first_month: Month
    _last_month: Month

    def __init__(self, start: MonthRange, end: MonthRange, strict: bool = False) -> None:
        if not isinstance(start, MonthRange):
            raise ValueError(f"invalid month range start: {start}")
        if not isinstance(end, MonthRange):
            raise ValueError(f"invalid month range end: {end}")
        first_month = start.first_month
        last_month = end.last_month
        if first_month <= last_month:
            self._first_month = first_month
            self._last_month = last_month
        elif not strict:
            self._first_month = last_month
            self._last_month = first_month
        else:
            raise ValueError("first_month after last_month")

    @classmethod
    def _abort_parse(cls, v: Any) -> Never:
        raise ValueError(f"unable to parse {v} as {cls.__name__}")

    @classmethod
    def parse(cls: Type[TS], v: Any, *, year_align: bool = True) -> TS:
        for aligned_type in cls.__year_aligned_types__:
            try:
                return aligned_type.parse(v)
            except ValueError:
                pass

        if isinstance(v, Mapping):
            start = None
            for key in v.keys():
                if key.lower() in ["start", "from", "min", "begin", "first"]:
                    start = cls.parse(v[key])
                    break
            if start is None:
                cls._abort_parse(v)

            end = None
            for key in v.keys():
                if key.lower() in ["end", "to", "max", "until", "last"]:
                    end = cls.parse(v[key])
                    break
            if end is None:
                cls._abort_parse(v)

            result = MonthRange(start=start, end=end)
            return result.year_align() if year_align else result

        elif isinstance(v, Sequence):
            if len(v) == 2:
                result = MonthRange(start=cls.parse(v[0]), end=cls.parse(v[1]))
                return result.year_align() if year_align else result

        cls._abort_parse(v)

    @property
    def month_count(self) -> int:
        first_month = self.first_month
        last_month = self.last_month
        if first_month.year == last_month.year:
            return last_month.index - first_month.index + 1
        return 13 - first_month.index + last_month.index + 12 * (last_month.year - first_month.year - 1)

    @property
    def first_month(self) -> Month:
        return self._first_month

    @property
    def last_month(self) -> Month:
        return self._last_month

    @property
    def first_day(self) -> date:
        return date(self.last_month.year, self.last_month.index, 1)

    @property
    def last_day(self) -> date:
        return date(
            self.last_month.year,
            self.last_month.index,
            monthrange(self.last_month.year, self.last_month.index)[1],
        )

    @property
    def first_moment(self) -> datetime:
        return datetime.combine(self.first_day, datetime.min.time(), tzinfo=ZoneInfo(TIMEZONE_NAME))

    @property
    def last_moment(self) -> datetime:
        return datetime.combine(self.last_day, datetime.max.time(), tzinfo=ZoneInfo(TIMEZONE_NAME))

    def next(self, offset: int = 1) -> MonthRange:
        if offset == 0:
            return self
        return MonthRange(
            start=self.first_month.next(offset=offset * self.month_count),
            end=self.last_month.next(offset=offset * self.month_count),
        )

    def prev(self, offset: int = 1) -> MonthRange:
        if offset == 0:
            return self
        return MonthRange(
            start=self.first_month.prev(offset=offset * self.month_count),
            end=self.last_month.prev(offset=offset * self.month_count),
        )

    def overlaps(self, other: MonthRange) -> bool:
        return (
            other.first_month in self
            or other.last_month in self
            or self.first_month in other
            or self.last_month in other
        )

    def adjacent_to(self, other: MonthRange) -> bool:
        return self.directly_after(other) or self.directly_before(other)

    def directly_after(self, other: MonthRange) -> bool:
        return self.first_month.prev() == other.last_month

    def directly_before(self, other: MonthRange) -> bool:
        return self.last_month.next() == other.first_month

    def touches(self, other: MonthRange) -> bool:
        return self.overlaps(other) or self.adjacent_to(other)

    def year_align(self) -> MonthRange:
        if self.first_month.year == self.last_month.year:
            last_month_index = self.last_month.index
            for aligned_type in MonthRange.__year_aligned_types__:
                if last_month_index % aligned_type.MONTH_COUNT == 0:
                    if last_month_index - aligned_type.MONTH_COUNT + 1 == self.first_month.index:
                        return aligned_type(self.first_month.year, last_month_index // aligned_type.MONTH_COUNT)
        return self

    @staticmethod
    def union_(*month_ranges: MonthRange, year_align: bool = True) -> List[MonthRange]:
        if len(month_ranges) == 0:
            return []
        result = []
        month_ranges = sorted(month_ranges, key=lambda t: t.first_month)
        prev = month_ranges[0]
        for month_range in month_ranges[1:]:
            if prev.overlaps(other=month_range) or month_range.directly_after(prev):
                prev = MonthRange(
                    start=min(prev.first_month, month_range.first_month),
                    end=max(prev.last_month, month_range.last_month),
                )
            else:
                result.append(prev)
                prev = month_range
        result.append(prev)
        return list(map(methodcaller("year_align"), result)) if year_align else result

    def union(self, *others: MonthRange, year_align: bool = True) -> List[MonthRange]:
        return self.union_(self, *others, year_align=year_align)

    @staticmethod
    def intersect_(*month_ranges: MonthRange, year_align: bool = True) -> MonthRange | None:
        if len(month_ranges) == 0:
            return None
        intersection = month_ranges[0]
        for month_range in month_ranges[1:]:
            if intersection.overlaps(other=month_range):
                intersection = MonthRange(
                    start=max(intersection.first_month, month_range.first_month),
                    end=min(intersection.last_month, month_range.last_month),
                )
            else:
                return None
        return intersection.year_align() if year_align else intersection

    def intersect(self, *others: MonthRange, year_align: bool = True) -> MonthRange | None:
        return self.intersect_(self, *others, year_align=year_align)

    def split(self, by: Type[YearAlignedMonthRange] = ..., year_align: bool = True) -> List[MonthRange]:
        result = []
        split_begin: Month = self.first_month
        last_month: Month = self.last_month
        if by in (Ellipsis, MonthRange.__atomic_type__):
            while split_begin <= last_month:
                result.append(split_begin)
                split_begin = split_begin.next()
            return result
        else:
            split = MonthRange(
                split_begin,
                MonthRange.__atomic_type__(
                    year=split_begin.year,
                    index=math.ceil(split_begin.index / by.MONTH_COUNT) * by.MONTH_COUNT,
                ),
            )
            while last_month not in split:
                result.append(split)
                split_begin = split.last_month.next()
                split = MonthRange(split_begin, split.last_month.next(offset=by.MONTH_COUNT))
            result.append(MonthRange(split_begin, last_month))
        return list(map(methodcaller("year_align"), result)) if year_align else result

    def _assert_comparable(self, other: Any) -> None:
        if not isinstance(other, MonthRange):
            raise ValueError(f"cannot compare {self.__class__.__name__} to {other.__class__.__name__}")

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return f"{self.first_month} ↔ {self.last_month}"

    def __hash__(self):
        return hash((self.first_month.year, self.first_month.index, self.last_month.year, self.last_month.index))

    def __len__(self) -> int:
        return self.month_count

    def __eq__(self, other: MonthRange) -> bool:
        self._assert_comparable(other)
        return (self.first_month.year, self.first_month.index, self.last_month.year, self.last_month.index) == (
            other.first_month.year,
            other.first_month.index,
            other.last_month.year,
            other.last_month.index,
        )

    def __contains__(self, other: MonthRange | datetime | date) -> bool:
        if isinstance(other, datetime | date):
            first_month = self.first_month
            last_month = self.last_month
            if other.year < first_month.year or other.year > last_month.year:
                return False
            if other.year == first_month.year and other.month < first_month.index:
                return False
            if other.year == last_month.year and other.month > first_month.index:
                return False
            return True
        self._assert_comparable(other)
        return other.first_month >= self.first_month and other.last_month <= self.last_month

    def _get_check_range(self, other: MonthRange | datetime | date) -> MonthRange:
        if isinstance(other, datetime | date):
            return self.__atomic_type__(other.year, other.month)
        else:
            self._assert_comparable(other)
            return other

    def __lt__(self, other: MonthRange | datetime | date) -> bool:
        check_month = self._get_check_range(other).first_month
        if self.last_month.year < check_month.year:
            return True
        if self.last_month.year == check_month.year:
            return self.last_month.index < check_month.index
        return False

    def __gt__(self, other: MonthRange | datetime | date) -> bool:
        check_month = self._get_check_range(other).last_month
        if self.first_month.year > check_month.year:
            return True
        if self.first_month.year == check_month.year:
            return self.first_month.index > check_month.index
        return False

    def __le__(self, other: MonthRange | datetime | date) -> bool:
        check_month = self._get_check_range(other).first_month
        if self.last_month.year < check_month.year:
            return True
        if self.last_month.year == check_month.year:
            return self.last_month.index <= check_month.index
        return False

    def __ge__(self, other: MonthRange | datetime | date) -> bool:
        check_month = self._get_check_range(other).last_month
        if self.first_month.year > check_month.year:
            return True
        if self.first_month.year == check_month.year:
            return self.first_month.index >= check_month.index
        return False

    def __add__(self, offset: int) -> MonthRange:
        return self.next(offset)

    def __sub__(self, offset: int) -> MonthRange:
        return self.prev(offset)

    def __or__(self, other: MonthRange) -> List[MonthRange]:
        return self.union_(self, other, year_align=True)

    def __and__(self, other: MonthRange) -> MonthRange | None:
        return self.intersect_(self, other, year_align=True)


#     todo xor
