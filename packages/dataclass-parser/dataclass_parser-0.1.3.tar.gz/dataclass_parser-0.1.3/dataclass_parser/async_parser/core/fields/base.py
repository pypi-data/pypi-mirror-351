from typing import Any

from dataclass_parser.core.errors import TypeMismatchError


class ASimpleFieldParser:
    __slots__ = ('args_parsers', 'origin')
    origin: type[Any]

    def __init__(self, origin: type[Any], args_parsers: list['ASimpleFieldParser'] | None):
        self.origin = origin
        self.args_parsers = args_parsers

    async def parse_value(self, value: Any) -> Any:
        try:
            return self.origin(value)
        except (ValueError, TypeError) as exc:
            msg = f'Failed to convert value: {exc!s}'
            raise TypeMismatchError(msg, value, self.origin) from exc

    async def dump_value(self, value: Any) -> Any:
        return value
