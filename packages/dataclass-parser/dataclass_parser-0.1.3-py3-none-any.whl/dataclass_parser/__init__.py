"""
Dataclass Parser - библиотека для удобного преобразования данных между 
Python dataclasses и другими форматами (JSON, ORM объекты и т.д.).
"""

__version__ = "0.1.3"

from dataclass_parser.core import EntityBase
from dataclass_parser.schema.generator import SchemaGenerator
from dataclass_parser import async_parser

__all__ = [
    "SchemaGenerator",
    "EntityBase",
    "async_parser"
]
