from typing import Any
from collections.abc import Sequence, Generator

from .base import SimpleFieldParser


class ListFieldParser(SimpleFieldParser):
    __slots__ = ()

    def _parse_value(self, value: Sequence[Any]) -> Generator[Any]:
        parser = self.args_parsers[0]
        return (parser.parse_value(item) for item in value)

    def _dump_value(self, value: Sequence[Any]) -> Generator[Any]:
        parser = self.args_parsers[0]
        return (parser.dump_value(item) for item in value)

    def parse_value(self, value: Sequence[Any]) -> list[Any]:
        result = self._parse_value(value)
        try:
            return self.origin(result)
        except Exception:
            return [*result]

    def dump_value(self, value: Sequence[Any]) -> list[Any]:
        return [*self._dump_value(value)]


class TupleFieldParser(ListFieldParser):
    __slots__ = ()

    def parse_value(self, value: Sequence[Any]) -> tuple[Any, ...]:
        return tuple(self._parse_value(value))

    def dump_value(self, value: Sequence[Any]) -> tuple[Any, ...]:
        return tuple(self._dump_value(value))


class SetFieldParser(ListFieldParser):
    __slots__ = ()

    def parse_value(self, value: Sequence[Any]) -> set[Any]:
        return set(self._parse_value(value))

    def dump_value(self, value: Sequence[Any]) -> set[Any]:
        return set(self._dump_value(value))
