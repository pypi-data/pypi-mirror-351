"""Core components for dataclass_parser."""

from dataclass_parser.core.base_entity import EntityBase
from dataclass_parser.core.base_mapper import TYPE_MAPPING_BASE
from dataclass_parser.core.errors import ParseError

__all__ = [
    "EntityBase",
    "TYPE_MAPPING_BASE",
    "ParseError",
]
