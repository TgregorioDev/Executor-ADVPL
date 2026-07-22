"""Native functions exposed to ADVPL programs."""

import math
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from src.errors.errors import TypeMismatch
from src.runtime.runtime import Runtime
from src.utils.helpers import format_value, is_numeric, normalize_name


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
                # --- Console / dialogs (simulated) ---
                BuiltinFunction("ConOut", 0, 1, self._conout),
                BuiltinFunction("MsgInfo", 0, 1, self._msginfo),
                BuiltinFunction("Alert", 0, 1, self._msginfo),
                BuiltinFunction("InputBox", 0, 1, self._inputbox),
                # --- Strings ---
                BuiltinFunction("Len", 1, 1, self._len),
                BuiltinFunction("Upper", 1, 1, self._upper),
                BuiltinFunction("Lower", 1, 1, self._lower),
                BuiltinFunction("AllTrim", 1, 1, self._alltrim),
                BuiltinFunction("SubStr", 2, 3, self._substr),
                BuiltinFunction("Left", 2, 2, self._left),
                BuiltinFunction("Right", 2, 2, self._right),
                BuiltinFunction("Str", 1, 3, self._str),
                BuiltinFunction("Val", 1, 1, self._val),
                BuiltinFunction("Empty", 1, 1, self._empty),
                # --- Numbers ---
                BuiltinFunction("Int", 1, 1, self._int),
                BuiltinFunction("Round", 2, 2, self._round),
                BuiltinFunction("Abs", 1, 1, self._abs),
                # --- Dates / time ---
                BuiltinFunction("Date", 0, 0, self._date),
                BuiltinFunction("Time", 0, 0, self._time),
                BuiltinFunction("CToD", 1, 1, self._ctod),
                BuiltinFunction("DToC", 1, 1, self._dtoc),
                # --- Arrays ---
                BuiltinFunction("AAdd", 2, 2, self._aadd),
                BuiltinFunction("ALen", 1, 1, self._alen),
                BuiltinFunction("ASize", 2, 2, self._asize),
                # --- Hashes (simple objects) ---
                BuiltinFunction("HB_HNew", 0, 0, self._hb_hnew),
                BuiltinFunction("HB_HHasKey", 2, 2, self._hb_hhaskey),
                BuiltinFunction("HB_HSet", 3, 3, self._hb_hset),
                BuiltinFunction("HB_HGet", 2, 3, self._hb_hget),
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

    def _inputbox(self, arguments: list[Any], runtime: Runtime) -> str:
        prompt = format_value(arguments[0]) if arguments else ""
        return runtime.read_input(prompt)

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
        # Str(value) simply formats the value. The optional length and decimals
        # arguments produce a right-justified numeric string, as in ADVPL.
        value = arguments[0]
        if len(arguments) == 1:
            return format_value(value)

        if not is_numeric(value):
            raise TypeMismatch("Str with length/decimals expects a number.")

        length = int(arguments[1])
        decimals = int(arguments[2]) if len(arguments) > 2 else 0
        if decimals > 0:
            text = f"{float(value):.{decimals}f}"
        else:
            text = str(int(round(value)))
        return text.rjust(length)

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

    # ------------------------------------------------------------------ #
    # String helpers                                                     #
    # ------------------------------------------------------------------ #
    def _substr(self, arguments: list[Any], _runtime: Runtime) -> str:
        text = arguments[0]
        if not isinstance(text, str):
            raise TypeMismatch("SubStr expects a string.")

        start = int(self._as_number(arguments[1], "SubStr start"))
        # ADVPL uses 1-based positions; a start below 1 begins at the first char.
        begin = max(start - 1, 0)
        if len(arguments) > 2:
            count = int(self._as_number(arguments[2], "SubStr length"))
            if count < 0:
                count = 0
            return text[begin : begin + count]
        return text[begin:]

    def _left(self, arguments: list[Any], _runtime: Runtime) -> str:
        text = arguments[0]
        if not isinstance(text, str):
            raise TypeMismatch("Left expects a string.")
        count = int(self._as_number(arguments[1], "Left length"))
        return text[: max(count, 0)]

    def _right(self, arguments: list[Any], _runtime: Runtime) -> str:
        text = arguments[0]
        if not isinstance(text, str):
            raise TypeMismatch("Right expects a string.")
        count = int(self._as_number(arguments[1], "Right length"))
        if count <= 0:
            return ""
        return text[-count:]

    def _empty(self, arguments: list[Any], _runtime: Runtime) -> bool:
        # Empty() reports whether a value is "blank" for its type.
        value = arguments[0]
        if value is None:
            return True
        if isinstance(value, bool):
            return not value
        if is_numeric(value):
            return value == 0
        if isinstance(value, str):
            return value.strip() == ""
        if isinstance(value, (list, dict)):
            return len(value) == 0
        return False

    # ------------------------------------------------------------------ #
    # Numeric helpers                                                    #
    # ------------------------------------------------------------------ #
    def _int(self, arguments: list[Any], _runtime: Runtime) -> int:
        return int(self._as_number(arguments[0], "Int"))

    def _round(self, arguments: list[Any], _runtime: Runtime) -> float | int:
        value = self._as_number(arguments[0], "Round")
        decimals = int(self._as_number(arguments[1], "Round decimals"))
        # ADVPL rounds halves away from zero (unlike Python's banker rounding).
        factor = 10 ** decimals
        rounded = math.floor(abs(value) * factor + 0.5) / factor
        rounded = math.copysign(rounded, value)
        return int(rounded) if decimals <= 0 else rounded

    def _abs(self, arguments: list[Any], _runtime: Runtime) -> float | int:
        return abs(self._as_number(arguments[0], "Abs"))

    # ------------------------------------------------------------------ #
    # Date / time helpers                                                #
    # ------------------------------------------------------------------ #
    def _date(self, _arguments: list[Any], _runtime: Runtime) -> date:
        return date.today()

    def _time(self, _arguments: list[Any], _runtime: Runtime) -> str:
        return datetime.now().strftime("%H:%M:%S")

    # ------------------------------------------------------------------ #
    # Array helpers                                                      #
    # ------------------------------------------------------------------ #
    def _alen(self, arguments: list[Any], _runtime: Runtime) -> int:
        array = arguments[0]
        if not isinstance(array, list):
            raise TypeMismatch("ALen expects an array.")
        return len(array)

    def _asize(self, arguments: list[Any], _runtime: Runtime) -> list[Any]:
        array = arguments[0]
        if not isinstance(array, list):
            raise TypeMismatch("ASize expects an array as the first argument.")
        size = int(self._as_number(arguments[1], "ASize size"))
        if size < 0:
            raise TypeMismatch("ASize size cannot be negative.")
        if size < len(array):
            del array[size:]
        else:
            array.extend([None] * (size - len(array)))
        return array

    # ------------------------------------------------------------------ #
    # Hash helpers (simple objects)                                      #
    # ------------------------------------------------------------------ #
    def _hb_hnew(self, _arguments: list[Any], _runtime: Runtime) -> dict[Any, Any]:
        return {}

    def _hb_hhaskey(self, arguments: list[Any], _runtime: Runtime) -> bool:
        hash_value = self._as_hash(arguments[0], "HB_HHasKey")
        return arguments[1] in hash_value

    def _hb_hset(self, arguments: list[Any], _runtime: Runtime) -> dict[Any, Any]:
        hash_value = self._as_hash(arguments[0], "HB_HSet")
        hash_value[arguments[1]] = arguments[2]
        return hash_value

    def _hb_hget(self, arguments: list[Any], _runtime: Runtime) -> Any:
        hash_value = self._as_hash(arguments[0], "HB_HGet")
        key = arguments[1]
        if key in hash_value:
            return hash_value[key]
        # A default value can be supplied as the optional third argument.
        if len(arguments) > 2:
            return arguments[2]
        raise TypeMismatch(f"HB_HGet: key {key!r} not found in hash.")

    # ------------------------------------------------------------------ #
    # Internal type guards                                               #
    # ------------------------------------------------------------------ #
    def _as_number(self, value: Any, context: str) -> int | float:
        if is_numeric(value):
            return value
        raise TypeMismatch(f"{context} expects a numeric value.")

    def _as_hash(self, value: Any, context: str) -> dict[Any, Any]:
        if isinstance(value, dict):
            return value
        raise TypeMismatch(f"{context} expects a hash.")
