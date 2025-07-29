from .month_range import MonthRange
from .year_aligned_month_range import YearAlignedMonthRange
from .year_aligned import Month, QuarterYear, Quadrimester, HalfYear, Year


# resolving circular deps. why do you make me do this python?
MonthRange.__atomic_type__ = Month
MonthRange.__year_aligned_types__ = (Month, QuarterYear, Quadrimester, HalfYear, Year)
