"""Native functions exposed to ADVPL programs."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from src.errors.errors import TypeMismatch
from src.runtime.runtime import Runtime
from src.utils.helpers import format_value, normalize_name


BuiltinHandler = Callable[[list[Any], Runtime], Any]


@dataclass(frozen=True)
class BuiltinFunction:
    """Metadata and handler for one built-in function."""

    name: str
    min_arity: int
    max_arity: int
    handler: BuiltinHandler

    def call(self, arguments: list[Any], runtime: Runtime) -> Any:
        """Validate arity and execute the built-in handler."""

        if not self.min_arity <= len(arguments) <= self.max_arity:
            if self.min_arity == self.max_arity:
                expected = str(self.min_arity)
            else:
                expected = f"{self.min_arity} to {self.max_arity}"
            raise TypeMismatch(
                f"{self.name} expects {expected} arguments, "
                f"got {len(arguments)}."
            )

        return self.handler(arguments, runtime)


class BuiltinRegistry:
    """Case-insensitive registry for the first set of ADVPL built-ins."""

    def __init__(self) -> None:
        self._functions = {
            normalize_name(item.name): item
            for item in (
                BuiltinFunction("ConOut", 0, 1, self._conout),
                BuiltinFunction("MsgInfo", 0, 1, self._msginfo),
                BuiltinFunction("Len", 1, 1, self._len),
                BuiltinFunction("Upper", 1, 1, self._upper),
                BuiltinFunction("Lower", 1, 1, self._lower),
                BuiltinFunction("AllTrim", 1, 1, self._alltrim),
                BuiltinFunction("Str", 1, 1, self._str),
                BuiltinFunction("Val", 1, 1, self._val),
                BuiltinFunction("AAdd", 2, 2, self._aadd),
                BuiltinFunction("CToD", 1, 1, self._ctod),
                BuiltinFunction("DToC", 1, 1, self._dtoc),
            )
        }

    def has(self, name: str) -> bool:
        """Return True when a built-in exists with this name."""

        return normalize_name(name) in self._functions

    def call(self, name: str, arguments: list[Any], runtime: Runtime) -> Any:
        """Execute a built-in function by name."""

        return self._functions[normalize_name(name)].call(arguments, runtime)

    def names(self) -> list[str]:
        """Return built-in names for documentation or diagnostics."""

        return sorted(function.name for function in self._functions.values())

    def _conout(self, arguments: list[Any], runtime: Runtime) -> None:
        runtime.write_output(format_value(arguments[0]) if arguments else "")
        return None

    def _msginfo(self, arguments: list[Any], runtime: Runtime) -> None:
        runtime.write_output(format_value(arguments[0]) if arguments else "")
        return None

    def _len(self, arguments: list[Any], _runtime: Runtime) -> int:
        value = arguments[0]
        if isinstance(value, (str, list)):
            return len(value)
        raise TypeMismatch("Len expects a string or an array.")

    def _upper(self, arguments: list[Any], _runtime: Runtime) -> str:
        value = arguments[0]
        if not isinstance(value, str):
            raise TypeMismatch("Upper expects a string.")
        return value.upper()

    def _lower(self, arguments: list[Any], _runtime: Runtime) -> str:
        value = arguments[0]
        if not isinstance(value, str):
            raise TypeMismatch("Lower expects a string.")
        return value.lower()

    def _alltrim(self, arguments: list[Any], _runtime: Runtime) -> str:
        value = arguments[0]
        if not isinstance(value, str):
            raise TypeMismatch("AllTrim expects a string.")
        return value.strip()

    def _str(self, arguments: list[Any], _runtime: Runtime) -> str:
        return format_value(arguments[0])

    def _val(self, arguments: list[Any], _runtime: Runtime) -> int | float:
        value = arguments[0]
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return value
        if not isinstance(value, str):
            raise TypeMismatch("Val expects a string or numeric value.")

        text = value.strip()
        if text == "":
            return 0

        try:
            if "." in text:
                return float(text)
            return int(text)
        except ValueError:
            return 0

    def _aadd(self, arguments: list[Any], _runtime: Runtime) -> list[Any]:
        array = arguments[0]
        if not isinstance(array, list):
            raise TypeMismatch("AAdd expects an array as the first argument.")
        array.append(arguments[1])
        return array

    def _ctod(self, arguments: list[Any], _runtime: Runtime) -> date | None:
        value = arguments[0]
        if not isinstance(value, str):
            raise TypeMismatch("CToD expects a string.")

        text = value.strip()
        if text == "":
            return None

        for pattern in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(text, pattern).date()
            except ValueError:
                continue

        raise TypeMismatch("CToD expects a date in DD/MM/YYYY or YYYY-MM-DD format.")

    def _dtoc(self, arguments: list[Any], _runtime: Runtime) -> str:
        value = arguments[0]
        if value is None:
            return ""
        if not isinstance(value, date):
            raise TypeMismatch("DToC expects a date value.")
        return value.strftime("%d/%m/%Y")
