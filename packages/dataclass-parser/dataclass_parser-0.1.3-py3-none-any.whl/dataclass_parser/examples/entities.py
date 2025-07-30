from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from uuid import UUID

from dataclass_parser.core.base_entity import EntityBase


@dataclass
class Data(EntityBase):
    name: str


@dataclass
class DataList(EntityBase):
    data_list: list[Data]


@dataclass
class DataOneToOne(EntityBase):
    data: Data


@dataclass
class DataOneToList(EntityBase):
    data_list: list[DataList]


@dataclass
class DateTimeEntity(EntityBase):
    created_at: datetime


@dataclass
class UUIDEntity(EntityBase):
    id: UUID


@dataclass
class OptionalValue(EntityBase):
    value: int | None


@dataclass
class UnionValue(EntityBase):
    value: int | str | float


@dataclass
class Nested(EntityBase):
    timestamp: datetime
    items: list['UUIDEntity']
    metadata: dict[str, int | str]


@dataclass
class Complex(EntityBase):
    created_at: date
    updated_at: time
    versions: tuple[float, ...]
    details: Nested


@dataclass
class MixedCollections(EntityBase):
    users: set[str]
    matrix: list[list[int]]


class Status(Enum):
    ACTIVE = 1
    INACTIVE = 0


@dataclass
class StatusEntity(EntityBase):
    value: Status


@dataclass
class Money(EntityBase):
    amount: Decimal
    currency: str


@dataclass
class TimeFormats(EntityBase):
    timestamp_str: datetime
    timestamp_int: datetime


@dataclass
class Document(EntityBase):
    id: UUID
    created_at: datetime
    content: str


@dataclass
class Settings(EntityBase):
    theme: str = 'dark'
    notifications: bool = True


@dataclass
class Age(EntityBase):
    value: int


@dataclass
class FileInfo(EntityBase):
    path: Path
    size: int


@dataclass
class MixedCollection(EntityBase):
    items: list[int | str | float]


@dataclass
class Matrix(EntityBase):
    rows: list[list[int]]


@dataclass
class AdvancedCollections(EntityBase):
    data: dict[str, list[list[int]] | set[int] | dict[str, list[dict]]]


@dataclass
class Recursion(EntityBase):
    data: list['Recursion']


@dataclass
class Department(EntityBase):
    employees: list['Employee']


@dataclass
class Employee(EntityBase):
    department: 'Department'
