"""Variable metadata used by runtime scopes."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class VariableKind(Enum):
    """ADVPL declaration kinds supported by the simplified runtime."""

    LOCAL = "LOCAL"
    STATIC = "STATIC"
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


@dataclass
class Variable:
    """A named runtime value plus the declaration kind that created it."""

    name: str
    kind: VariableKind
    value: Any
