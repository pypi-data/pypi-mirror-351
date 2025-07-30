from __future__ import annotations

from dataclasses import fields
from typing import TYPE_CHECKING, Any

from .base import SimpleFieldParser

if TYPE_CHECKING:
    from ..base_entity import EntityBase
    from collections.abc import Sequence


class EntityFieldParser(SimpleFieldParser):
    __slots__ = ()
    origin: type[EntityBase]

    def parse_value(self, value: Any) -> EntityBase:
        entity_data = {}
        for field in fields(self.origin):
            try:
                field_value = getattr(value, field.name)
            except AttributeError:
                field_value = value.get(field.name)

            entity_data[field.name] = (
                None if field_value is None else self.origin.schema[field.name].parse_value(field_value)
            )
        return self.origin(**entity_data)

    def dump_value(
        self, value: EntityBase, *, exclude: Sequence[str] | None = None, exclude_none: bool = False
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if not exclude:
            exclude = ()
        for field in fields(self.origin):
            field_name = field.name
            if field_name in exclude:
                continue
            field_value = getattr(value, field_name)
            if exclude_none and field_value is None:
                continue
            data[field_name] = self.origin.schema[field_name].dump_value(field_value)
        return data
