# month-range

A Python package for handling and manipulating date ranges at the month level.

## Overview

`month-range` provides a clean, intuitive API for working with date ranges at the month level. It's particularly useful for:

- Financial reporting periods
- Academic terms and semesters
- Business quarters and fiscal years
- Project timeline management
- Subscription periods

The package brings the power of Python's standard datetime handling to month-level operations with an easy-to-use, chainable API.

## Installation

```bash
pip install month-range
```

## Features
- Create and manipulate month ranges easily
- Represent individual months, quarters, half-years, and full years
- Handle date arithmetic (add/subtract months, compare ranges)
- Calculate intersections and unions of date ranges
- Detect overlaps and adjacency between ranges
- Simplify arbitrary ranges into standard periods (months, quarters, etc.)
- Parse from and convert to various formats (strings, integers, etc.)

## Basic Usage

```python
from month_range import Month, MonthRange, Year, QuarterYear, HalfYear

# Create a month (multiple formats supported)
jan_2023 = Month.parse("2023-01")
feb_2023 = Month.parse(202302)  # YYYYMM format
current_month = Month.current()  # Current month

# Create a range
q1_2023 = MonthRange.parse(["2023-01", "2023-03"])
fiscal_year = MonthRange(Month(2023, 4), Month(2024, 3))

# Check if ranges overlap
if q1_2023.overlaps(fiscal_year):
  print("Ranges overlap")

# Get intersection
overlap = q1_2023 & fiscal_year  # Using operator
# or
overlap = q1_2023.intersect(fiscal_year)  # Using method

# Get all months in a range
months = fiscal_year.months  # Returns a list of Month objects

# Simplify standard periods
quarter = MonthRange(Month(2025, 1), Month(2025, 3)).year_align()  # Returns a QuarterYear
print(isinstance(quarter, QuarterYear))  # True

# Move ranges forward or backward
next_quarter = q1_2023 + 1  # Q2 2023
previous_quarter = q1_2023 - 1  # Q4 2022

# Compare ranges
if MonthRange(Month(2025, 1), Month(2025, 3)) == QuarterYear(2025, 1):
  print("These are the same period")
```

## Class Hierarchy

- `MonthRange`: Base class for all date ranges
  - `YearAlignedMonthRange`: Base class for all date ranges that are aligned to a calendar year
    - `Month`: Represents a single month
    - `QuarterYear`: Represents a fiscal quarter (3 months)
    - `HalfYear`: Represents half a year (6 months)
    - `Year`: Represents a full calendar year (12 months)

## Advanced Usage

### Working with Custom Business Logic

```python
# Check if a range follows directly after another
q1 = QuarterYear(2023, 1)
q2 = QuarterYear(2023, 2)

if q2.follows_directly(q1):
    print("Q2 follows Q1 directly")

# Check containment
fiscal_year = MonthRange("2023-01", "2023-12")
q3 = QuarterYear(2023, 3)

if q3 in fiscal_year:
    print("Q3 is within the fiscal year")
```

## API Reference

### `Month`

```python
# Initialization formats
month = Month.current()  # Current month
month = Month(2025, 4)  # From year and month

month.year == 2025  # year as int
month.index == 4  # month as int from 1 to 12

str(month) == "2025-04"
```

### `MonthRange`

```python
# Initialize with Month objects, strings, or integers
range = MonthRange(Month("2023-01"), Month("2023-12"))
range = MonthRange("2023-01", "2023-12")
range = MonthRange(202301, 202312)

# Properties
first = range.first_month  # First month in range
last = range.last_month  # Last month in range
count = range.month_count  # Number of months in range
all_months = range.months  # List of all Month objects in range

# Methods
simplified = range.year_align()  # Convert to most specific type
next_range = range.next()  # Move range forward by its own length
prev_range = range.prev(2)  # Move range backward by twice its length
has_overlap = range.overlaps(other_range)  # Check for overlap
is_following = range.directly_after(other_range)  # Check adjacency
intersection = range.intersect(other_range)  # Get intersection
unions = range.union(other_range1, other_range2)  # Get union
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT license.