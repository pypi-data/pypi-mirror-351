from typing import Literal, Tuple

from ..year_aligned_month_range import YearAlignedMonthRange


class QuarterYear(YearAlignedMonthRange[Literal[1, 2, 3, 4]]):
    MONTH_COUNT: Literal[3] = 3
    SERIALIZATION_KEYS: Tuple[str, ...] = "quarter", "quart", "q"
