import math
from decimal import Decimal
from fractions import Fraction
from typing import Mapping, Collection, Any, Iterable


def unpack_nested(v: Any, keywords: Iterable[str]) -> Any:
    if isinstance(v, Mapping):
        for key in v.keys():
            if key.lower() in keywords:
                return unpack_nested(v[key], keywords)

    elif isinstance(v, Collection) and len(v) == 1:
        return unpack_nested(next(iter(v)), keywords)

    return v


YEAR_SERIALIZATION_KEYS = ["year", "y"]


def parse_year_int(v: Any) -> int:
    original_v = v
    v = unpack_nested(v, YEAR_SERIALIZATION_KEYS)

    if isinstance(v, int):
        return v

    if isinstance(v, str):
        v = v.strip()
        if v.isdigit():
            return int(v)

    elif isinstance(v, float | Decimal | Fraction):
        return int(math.floor(v))

    raise ValueError(f"unable to parse {original_v} as year")
