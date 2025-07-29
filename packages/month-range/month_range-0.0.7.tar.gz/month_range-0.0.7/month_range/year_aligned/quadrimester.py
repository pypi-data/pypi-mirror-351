from typing import Literal, Tuple

from ..year_aligned_month_range import YearAlignedMonthRange


class Quadrimester(YearAlignedMonthRange[Literal[1, 2, 3]]):
    MONTH_COUNT: Literal[4] = 4
    SERIALIZATION_KEYS: Tuple[str, ...] = "tri", "t"
