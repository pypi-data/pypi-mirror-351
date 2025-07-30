from typing import Any
from collections.abc import Sequence

from dataclass_parser.core.errors import EntityNotLoadedError
from dataclass_parser.async_parser.core.fields.base import ASimpleFieldParser
from dataclass_parser.async_parser.core.fields.entity import AEntityFieldParser
from dataclass_parser.async_parser.schema.generator import ASchemaGenerator


class AEntityBase:
    parser: AEntityFieldParser
    schema: dict[str, ASimpleFieldParser]

    @classmethod
    async def set_schema(cls, schema: dict[str, ASimpleFieldParser]) -> None:
        cls.schema = schema

    @classmethod
    async def check_context(cls) -> AEntityFieldParser:
        if not getattr(cls, 'schema', None):
            try:
                await cls.set_schema(await ASchemaGenerator.generate_schema(cls))
            except (TypeError, ValueError, AttributeError) as exc:
                msg = f'Failed to generate schema: {exc!s}'
                raise EntityNotLoadedError(msg) from exc

        if not getattr(cls, 'parser', None):
            cls.parser = AEntityFieldParser(cls, None)
        return cls.parser

    @classmethod
    async def parse(cls, orm_instance: Any) -> 'AEntityBase':
        return await (await cls.check_context()).parse_value(orm_instance)

    async def serialize(self, *, exclude: Sequence[str] | None = None, exclude_none: bool = False) -> dict[str, Any]:
        return await (await self.check_context()).dump_value(self)
