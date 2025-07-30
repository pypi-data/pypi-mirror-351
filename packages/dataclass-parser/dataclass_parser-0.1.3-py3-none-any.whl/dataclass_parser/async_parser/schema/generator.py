from __future__ import annotations

import asyncio
import sys
from dataclasses import fields, is_dataclass
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    ForwardRef,
    Union,
    get_args,
    get_origin,
)

from dataclass_parser.async_parser.core.base_mapper import TYPE_MAPPING_BASE
from dataclass_parser.async_parser.core.fields.entity import AEntityFieldParser

if TYPE_CHECKING:
    from dataclass_parser.async_parser.core.base_entity import AEntityBase

from dataclass_parser.async_parser.core.fields.base import ASimpleFieldParser
from dataclass_parser.async_parser.core.fields.complex import AUnionFieldParser


class ASchemaGenerator:
    __slots__ = ()
    TYPE_MAPPING: ClassVar[dict[type[Any], type[ASimpleFieldParser]]] = TYPE_MAPPING_BASE
    MAX_RECURSION_DEPTH: ClassVar[int] = 3  # Lower default to catch recursive structures faster
    _current_recursion_depth: ClassVar[dict[type[Any], int]] = {}

    @classmethod
    async def _resolve_forward_refs(cls, type_hint: type[Any], module: str) -> type[Any]:
        if isinstance(type_hint, (ForwardRef, str)):
            type_hint = type_hint if isinstance(type_hint, str) else type_hint.__forward_arg__
            try:
                module = sys.modules[module]
                return getattr(module, type_hint.split('.')[-1])
            except (NameError, SyntaxError) as exc:
                msg = f"Can't resolve forward reference {type_hint!s}"
                raise ValueError(msg) from exc
        return type_hint

    @classmethod
    async def _resolve_type(cls, type_hint: type[Any], module: str) -> tuple[type[Any], tuple[type[Any], ...]]:
        resolved_type = await cls._resolve_forward_refs(type_hint, module)
        base_type = get_origin(resolved_type) or resolved_type
        return base_type, await cls.filter_args(get_args(type_hint))

    @classmethod
    async def _get_parser_cls(cls, type_hint: type[Any], module: str) -> ASimpleFieldParser:
        base_type, type_args = await cls._resolve_type(type_hint, module)

        if base_type is Union or base_type is UnionType:
            return AUnionFieldParser(
                type_hint,
                await asyncio.gather(*[cls._get_parser_cls(type_, module) for type_ in type_args]),
            )

        if is_dataclass(base_type) and hasattr(base_type, 'set_schema'):
            current_depth = cls._current_recursion_depth.get(base_type, 0)

            if current_depth >= cls.MAX_RECURSION_DEPTH:
                return await cls._get_ellipsis_parser(type_hint)

            cls._current_recursion_depth[base_type] = current_depth + 1

            await base_type.set_schema(await cls.generate_schema(base_type))
            return AEntityFieldParser(base_type, None)

        for field_type in cls.TYPE_MAPPING:
            if issubclass(base_type, field_type):
                return cls.TYPE_MAPPING[field_type](
                    base_type,
                    await asyncio.gather(*[cls._get_parser_cls(type_, module) for type_ in type_args]) or None,
                )
        msg = f"Can't find field parser for type {base_type!s}"
        raise ValueError(msg)

    @classmethod
    async def _get_ellipsis_parser(cls, type_hint: type[Any]) -> ASimpleFieldParser:
        base_type = get_origin(type_hint) or type_hint

        parser_cls = type(
            'EllipsisParser',
            (ASimpleFieldParser,),
            {
                '__init__': lambda self, origin, _: setattr(self, 'origin', origin),
                'parse_value': lambda self, value: ...,
                'dump_value': lambda self, value: ...,
            },
        )
        parser = parser_cls(base_type, None)

        return parser

    @classmethod
    async def generate_schema(cls, entity: type[AEntityBase]) -> dict[str, ASimpleFieldParser]:
        schema: dict[str, ASimpleFieldParser] = {}
        for field in fields(entity):
            parser = await cls._get_parser_cls(field.type, entity.__module__)
            schema[field.name] = parser
        return schema

    @classmethod
    async def filter_args(cls, args: tuple[type[Any], ...]) -> tuple[type[Any], ...]:
        return tuple(arg for arg in args if arg is not type(None) and arg is not Ellipsis)
