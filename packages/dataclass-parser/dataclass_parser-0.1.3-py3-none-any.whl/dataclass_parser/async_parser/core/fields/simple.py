from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID

from dataclass_parser.core.errors import TypeMismatchError
from .base import ASimpleFieldParser


class ABoolFieldParser(ASimpleFieldParser):
    __slots__ = ()

    async def parse_value(self, value: Any) -> bool:
        if not isinstance(value, bool):
            msg = 'Value is not a boolean'
            raise TypeMismatchError(msg, value, bool)
        return value


class AUUIDFieldParser(ASimpleFieldParser):
    __slots__ = ()

    async def parse_value(self, value: UUID | str) -> UUID:
        try:
            return UUID(str(value))
        except ValueError as e:
            msg = 'Invalid UUID format'
            raise TypeMismatchError(msg, value, UUID) from e

    async def dump_value(self, value: str | UUID) -> str:
        return str(value)


class ADateTimeFieldParser(ASimpleFieldParser):
    __slots__ = ()

    async def parse_value(self, value: datetime | str) -> datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        else:
            return value

    async def dump_value(self, value: datetime) -> str:
        return value.isoformat()


class ADateFieldParser(ASimpleFieldParser):
    __slots__ = ()

    async def parse_value(self, value: date | str) -> date:
        if isinstance(value, str):
            return date.fromisoformat(value)
        else:
            return value

    async def dump_value(self, value: date) -> str:
        return value.isoformat()


class ATimeFieldParser(ASimpleFieldParser):
    __slots__ = ()

    async def parse_value(self, value: time | str) -> time:
        if isinstance(value, str):
            return time.fromisoformat(value)
        else:
            return value

    async def dump_value(self, value: time) -> str:
        return value.isoformat()


class AEnumFieldParser(ASimpleFieldParser):
    async def parse_value(self, value: str) -> Enum:
        return getattr(self.origin, value)


class ADecimalFieldParser(ASimpleFieldParser):
    async def parse_value(self, value: Decimal | str | int) -> Decimal:
        return Decimal(str(value))


class APathFieldParser(ASimpleFieldParser):
    async def parse_value(self, value: str | Path) -> Path:
        return Path(str(value))

    async def dump_value(self, value: Path) -> str:
        return str(value)
