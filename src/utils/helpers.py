"""Small helper functions shared by lexer, runtime, built-ins and interpreter."""

from datetime import date
from typing import Any


def normalize_name(name: str) -> str:
    """ADVPL names are treated case-insensitively in this executor."""

    return name.upper()


def is_numeric(value: Any) -> bool:
    """Return True for int and float values, excluding logical values."""

    return type(value) in {int, float}


def is_truthy(value: Any) -> bool:
    """Convert a Python value to the simplified logical semantics of ADVPL."""

    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if is_numeric(value):
        return value != 0
    if isinstance(value, (str, list)):
        return len(value) > 0
    return True


def format_value(value: Any) -> str:
    """Format runtime values for ConOut, MsgInfo and string concatenation."""

    if value is None:
        return ""
    if isinstance(value, bool):
        return ".T." if value else ".F."
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, list):
        return "{" + ", ".join(format_value(item) for item in value) + "}"
    return str(value)

