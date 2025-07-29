from typing import Literal, Tuple

from ..year_aligned_month_range import YearAlignedMonthRange


class HalfYear(YearAlignedMonthRange[Literal[1, 2]]):
    MONTH_COUNT: Literal[6] = 6
    SERIALIZATION_KEYS: Tuple[str, ...] = "half", "h"
