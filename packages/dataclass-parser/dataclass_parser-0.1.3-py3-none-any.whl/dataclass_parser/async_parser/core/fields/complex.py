from typing import Any

from dataclass_parser.core.errors import TypeMismatchError
from .base import ASimpleFieldParser


class AUnionFieldParser(ASimpleFieldParser):
    __slots__ = ()

    async def parse_value(self, value: Any) -> Any:
        for parser in self.args_parsers:
            try:
                return await parser.parse_value(value)
            except Exception:
                pass

        msg = 'Cannot determine appropriate type'
        raise TypeMismatchError(msg, value, self.origin)

    async def dump_value(self, value: Any) -> Any:
        for parser in self.args_parsers:
            try:
                return await parser.dump_value(value)
            except Exception:
                pass
        return value
