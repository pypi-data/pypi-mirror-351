from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal, Tuple

from ..year_aligned_month_range import YearAlignedMonthRange
from ..parse_util import parse_year_int, YEAR_SERIALIZATION_KEYS


class Year(YearAlignedMonthRange[Literal[1]]):
    MONTH_COUNT: Literal[12] = 12
    SERIALIZATION_KEYS: Tuple[str, ...] = YEAR_SERIALIZATION_KEYS

    def __init__(self, year: int, index: int = 1) -> None:
        super().__init__(year=year, index=index)

    @classmethod
    def parse(cls, v: Any, *, year_align: bool = True) -> Year:
        if isinstance(v, date | datetime):
            return cls(v.year)
        try:
            return cls(parse_year_int(v))
        except Exception:
            pass
        cls._abort_parse(v)

    def __str__(self) -> str:
        return str(self.year)

    # the following methods are redefined here for performance reasons
    @property
    def index(self) -> Literal[1]:
        return 1

    @classmethod
    def current(cls) -> Year:
        return cls(date.today().year)
