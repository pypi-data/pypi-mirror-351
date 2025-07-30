from collections.abc import Iterable
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Any
from collections.abc import Sequence
from uuid import UUID

from dataclass_parser.async_parser.core.fields.base import ASimpleFieldParser
from dataclass_parser.async_parser.core.fields.collections import (
    AListFieldParser,
    ASetFieldParser,
    ATupleFieldParser,
)
from dataclass_parser.async_parser.core.fields.complex import AUnionFieldParser
from dataclass_parser.async_parser.core.fields.simple import (
    ABoolFieldParser,
    ADateFieldParser,
    ADateTimeFieldParser,
    ADecimalFieldParser,
    AEnumFieldParser,
    APathFieldParser,
    ATimeFieldParser,
    AUUIDFieldParser,
)

TYPE_MAPPING_BASE: dict[type[Any], type[ASimpleFieldParser]] = {
    str: ASimpleFieldParser,
    bool: ABoolFieldParser,
    UUID: AUUIDFieldParser,
    int: ASimpleFieldParser,
    float: ASimpleFieldParser,
    complex: ASimpleFieldParser,
    bytes: ASimpleFieldParser,
    range: ASimpleFieldParser,
    dict: ASimpleFieldParser,
    datetime: ADateTimeFieldParser,
    date: ADateFieldParser,
    time: ATimeFieldParser,
    tuple: ATupleFieldParser,
    set: ASetFieldParser,
    Iterable: AListFieldParser,
    Sequence: AListFieldParser,
    UnionType: AUnionFieldParser,
    Enum: AEnumFieldParser,
    Decimal: ADecimalFieldParser,
    Path: APathFieldParser,
}
