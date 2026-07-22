"""Runtime scopes and symbol tables."""

from typing import Any

from src.runtime.variables import Variable, VariableKind
from src.utils.helpers import normalize_name


class Scope:
    """A symbol table for variables declared in one visibility area."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._values: dict[str, Variable] = {}

    def define(self, name: str, kind: VariableKind, value: Any) -> None:
        """Create or replace a variable in this exact scope."""

        self._values[normalize_name(name)] = Variable(name, kind, value)

    def contains(self, name: str) -> bool:
        """Return True when this scope directly owns the variable."""

        return normalize_name(name) in self._values

    def get(self, name: str) -> Any:
        """Read a variable value from this exact scope."""

        return self._values[normalize_name(name)].value

    def assign(self, name: str, value: Any) -> None:
        """Assign a variable value in this exact scope."""

        self._values[normalize_name(name)].value = value

    def snapshot(self) -> dict[str, Any]:
        """Return a simple view useful for tests and debugging."""

        return {variable.name: variable.value for variable in self._values.values()}
