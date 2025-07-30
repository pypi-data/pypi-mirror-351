"""
Exceptions module for dataclass_parser.

This module contains all the exceptions used in the dataclass_parser library.
"""

from typing import Any


class ParseError(Exception):
    """Exception raised when entity cannot be loaded.

    This exception is raised when an entity cannot be loaded from a source.
    It may happen when:
    - The schema is not set
    - The parser is not set
    - The parser fails to parse the value
    """

    entity: type | None
    source: Any

    def __init__(self, message: str, entity: type | None = None, source: Any = None):
        super().__init__(message)
        self.entity = entity
        self.source = source


class ParsingError(Exception):
    """Base exception for parsing errors."""

    def __init__(self, message: str, value: Any, expected_type: type[Any]):
        self.value = value
        self.expected_type = expected_type
        super().__init__(f'{message}. Value: {value}, Expected type: {expected_type}')


class TypeMismatchError(ParsingError):
    """Raised when value type doesn't match expected type."""

    pass


class EntityNotLoadedError(Exception):
    """Raised when called load or dumb on entity, but schema is not set"""

    pass


class DataclassIsNotEntityError(Exception):
    """Raised when try to generate schema for an entity,
    but it not a BaseEntity subclass"""

    pass
