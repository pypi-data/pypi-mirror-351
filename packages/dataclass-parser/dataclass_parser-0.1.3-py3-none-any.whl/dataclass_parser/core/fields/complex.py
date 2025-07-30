from typing import Any

from ..errors import TypeMismatchError
from .base import SimpleFieldParser


class UnionFieldParser(SimpleFieldParser):
    __slots__ = ()

    def parse_value(self, value: Any) -> Any:
        for parser in self.args_parsers:
            try:
                return parser.parse_value(value)
            except Exception:
                pass

        msg = 'Cannot determine appropriate type'
        raise TypeMismatchError(msg, value, self.origin)

    def dump_value(self, value: Any) -> Any:
        for parser in self.args_parsers:
            try:
                return parser.dump_value(value)
            except Exception:
                pass
        return value
