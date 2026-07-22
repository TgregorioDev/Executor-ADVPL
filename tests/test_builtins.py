import unittest
from datetime import date

from src.errors.errors import TypeMismatch
from src.functions.builtin import BuiltinRegistry
from src.runtime.runtime import Runtime


class BuiltinTest(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = BuiltinRegistry()
        self.runtime = Runtime()

    def test_conout_writes_to_runtime_output(self) -> None:
        self.registry.call("ConOut", ["Teste"], self.runtime)
        self.assertEqual(self.runtime.output, ["Teste"])

    def test_len_supports_strings_and_arrays(self) -> None:
        self.assertEqual(self.registry.call("Len", ["abc"], self.runtime), 3)
        self.assertEqual(self.registry.call("Len", [[1, 2]], self.runtime), 2)

    def test_aadd_mutates_array(self) -> None:
        values: list[str] = []
        self.registry.call("AAdd", [values, "novo"], self.runtime)
        self.assertEqual(values, ["novo"])

    def test_ctod_and_dtoc_simulate_dates(self) -> None:
        parsed = self.registry.call("CToD", ["22/07/2026"], self.runtime)
        self.assertEqual(parsed, date(2026, 7, 22))
        self.assertEqual(
            self.registry.call("DToC", [parsed], self.runtime),
            "22/07/2026",
        )

    def test_upper_rejects_non_string(self) -> None:
        with self.assertRaises(TypeMismatch):
            self.registry.call("Upper", [10], self.runtime)


if __name__ == "__main__":
    unittest.main()
