from datetime import date

import pytest

from month_range import Month, MonthRange, QuarterYear


def test_init():
    with pytest.raises(Exception):
        Month(None, None)

    with pytest.raises(Exception):
        Month(2025, None)

    with pytest.raises(Exception):
        Month(None, 1)

    with pytest.raises(Exception):
        Month("2025", "1")

    with pytest.raises(Exception):
        Month("2025", 1)

    with pytest.raises(Exception):
        Month(None, "1")

    month = Month(2025, 1)
    assert month.year == 2025
    assert month.index == 1

    month = Month(2025, 13)
    assert month.year == 2026
    assert month.index == 1

    month = Month(2025, 0)
    assert month.year == 2024
    assert month.index == 12

    month = Month(2025, 0)
    assert month.year == 2024
    assert month.index == 12


def test_parse():
    for v in [202501, "202501", "2025-01", "2025-m01"]:
        month = Month.parse(v)
        assert month.year == 2025
        assert month.index == 1

    for v in [202500, "202500", "unknown", "2025-m123"]:
        with pytest.raises(Exception):
            Month.parse(v)


def test_offset():
    month = Month(2025, 1)
    assert month.next().year == 2025
    assert month.next().index == 2
    assert month.year == 2025
    assert month.index == 1

    assert month.prev().year == 2024
    assert month.prev().index == 12
    assert month.year == 2025
    assert month.index == 1

    assert month.next(0).year == 2025
    assert month.next(0).index == 1
    assert month.year == 2025
    assert month.index == 1

    assert month.prev(0).year == 2025
    assert month.prev(0).index == 1
    assert month.year == 2025
    assert month.index == 1

    assert month.next(2).year == 2025
    assert month.next(2).index == 3
    assert month.year == 2025
    assert month.index == 1

    assert month.prev(2).year == 2024
    assert month.prev(2).index == 11
    assert month.year == 2025
    assert month.index == 1

    assert month.next(12).year == 2026
    assert month.next(12).index == 1
    assert month.year == 2025
    assert month.index == 1

    assert month.prev(13).year == 2023
    assert month.prev(13).index == 12
    assert month.year == 2025
    assert month.index == 1

    assert month.next(-1).year == 2024
    assert month.next(-1).index == 12
    assert month.year == 2025
    assert month.index == 1

    assert month.prev(-1).year == 2025
    assert month.prev(-1).index == 2
    assert month.year == 2025
    assert month.index == 1

    assert (month + 1).year == 2025
    assert (month + 1).index == 2
    assert month.year == 2025
    assert month.index == 1

    assert (month - 1).year == 2024
    assert (month - 1).index == 12
    assert month.year == 2025
    assert month.index == 1


def test_current():
    today = date.today()
    assert Month.current().index == today.month
    assert Month.current().year == today.year
    assert Month.current() == Month.parse(today)
    assert today in Month.current()


def test_comparison():
    assert Month(2025, 1) == Month(2025, 1)
    assert Month(2025, 1) <= Month(2025, 1)
    assert Month(2025, 1) >= Month(2025, 1)
    assert Month(2025, 1) != Month(2025, 2)
    assert Month(2025, 1) < Month(2025, 2)
    assert Month(2025, 2) > Month(2025, 1)


def test_set_ops():
    assert Month(2025, 1) | Month(2025, 1) == [Month(2025, 1)]
    assert Month(2025, 1) | Month(2025, 2) == [MonthRange(Month(2025, 1), Month(2025, 2))]
    assert Month(2025, 1) | Month(2025, 3) == [Month(2025, 1), Month(2025, 3)]
    assert Month(2025, 3) | Month(2025, 1) == [Month(2025, 1), Month(2025, 3)]
    assert Month(2025, 1).union(Month(2025, 2), Month(2025, 3)) == [QuarterYear(2025, 1)]

    assert Month(2025, 1) & Month(2025, 1) == Month(2025, 1)
    assert (Month(2025, 1) & Month(2025, 1)).__class__ == Month
    assert Month(2025, 1) & Month(2025, 2) is None
    assert Month(2025, 1) & QuarterYear(2025, 1) == Month(2025, 1)

    assert Month(2025, 1) in QuarterYear(2025, 1)
    assert QuarterYear(2025, 1) not in Month(2025, 1)
