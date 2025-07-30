from __future__ import annotations

import asyncio
from dataclasses import fields
from typing import TYPE_CHECKING, Any

from .base import ASimpleFieldParser

if TYPE_CHECKING:
    from ..base_entity import AEntityBase
    from collections.abc import Sequence


class AEntityFieldParser(ASimpleFieldParser):
    __slots__ = ()
    origin: type[AEntityBase]

    async def parse_value(self, value: Any) -> AEntityBase:
        entity_data = {}
        for field in fields(self.origin):
            try:
                field_value = getattr(value, field.name)
            except AttributeError:
                field_value = value.get(field.name)

            entity_data[field.name] = (
                None if field_value is None else await self.origin.schema[field.name].parse_value(field_value)
            )
        return self.origin(**entity_data)

    async def dump_value(
        self, value: AEntityBase, *, exclude: Sequence[str] | None = None, exclude_none: bool = False
    ) -> dict[str, Any]:
        tasks = []
        result = {}
        entity_fields = fields(self.origin)
        if not exclude:
            exclude = ()

        for field in entity_fields:
            if field.name not in exclude:
                tasks.append(asyncio.create_task(self.origin.schema[field.name].dump_value(getattr(value, field.name))))
        values = await asyncio.gather(*tasks)
        for i, field in enumerate(entity_fields):
            if not exclude_none and (dumped_value := values[i]) is not None:
                result[field.name] = dumped_value

        return result
