import asyncio
from typing import Any
from collections.abc import Sequence

from .base import ASimpleFieldParser


class AListFieldParser(ASimpleFieldParser):
    __slots__ = ()

    async def _parse_value(self, value: Sequence[Any]) -> list[Any]:
        parser = self.args_parsers[0]
        return await asyncio.gather(*(parser.parse_value(item) for item in value))

    async def _dump_value(self, value: Sequence[Any]) -> list[Any]:
        parser = self.args_parsers[0]
        return await asyncio.gather(*(parser.dump_value(item) for item in value))

    async def parse_value(self, value: Sequence[Any]) -> list[Any]:
        result = await self._parse_value(value)
        try:
            return self.origin(result)
        except Exception:
            return result

    async def dump_value(self, value: Sequence[Any]) -> list[Any]:
        return await self._dump_value(value)


class ATupleFieldParser(AListFieldParser):
    __slots__ = ()

    async def parse_value(self, value: Sequence[Any]) -> tuple[Any, ...]:
        return tuple(await self._parse_value(value))

    async def dump_value(self, value: Sequence[Any]) -> tuple[Any, ...]:
        return tuple(await self._dump_value(value))


class ASetFieldParser(AListFieldParser):
    __slots__ = ()

    async def parse_value(self, value: Sequence[Any]) -> set[Any]:
        return set(await self._parse_value(value))

    async def dump_value(self, value: Sequence[Any]) -> set[Any]:
        return set(await self._dump_value(value))
