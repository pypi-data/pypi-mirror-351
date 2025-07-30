from collections.abc import Iterable
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Any
from collections.abc import Sequence
from uuid import UUID

from dataclass_parser.core.fields.base import SimpleFieldParser
from dataclass_parser.core.fields.collections import (
    ListFieldParser,
    SetFieldParser,
    TupleFieldParser,
)
from dataclass_parser.core.fields.complex import UnionFieldParser
from dataclass_parser.core.fields.simple import (
    BoolFieldParser,
    DateFieldParser,
    DateTimeFieldParser,
    DecimalFieldParser,
    EnumFieldParser,
    PathFieldParser,
    TimeFieldParser,
    UUIDFieldParser,
)

TYPE_MAPPING_BASE: dict[type[Any], type[SimpleFieldParser]] = {
    str: SimpleFieldParser,
    bool: BoolFieldParser,
    UUID: UUIDFieldParser,
    int: SimpleFieldParser,
    float: SimpleFieldParser,
    complex: SimpleFieldParser,
    bytes: SimpleFieldParser,
    range: SimpleFieldParser,
    dict: SimpleFieldParser,
    datetime: DateTimeFieldParser,
    date: DateFieldParser,
    time: TimeFieldParser,
    tuple: TupleFieldParser,
    set: SetFieldParser,
    Iterable: ListFieldParser,
    Sequence: ListFieldParser,
    UnionType: UnionFieldParser,
    Enum: EnumFieldParser,
    Decimal: DecimalFieldParser,
    Path: PathFieldParser,
}
