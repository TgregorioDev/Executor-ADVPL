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

    def test_inputbox_returns_provided_value(self) -> None:
        prompts: list[str] = []

        def provider(prompt: str) -> str:
            prompts.append(prompt)
            return "Maria"

        runtime = Runtime(input_provider=provider)
        result = self.registry.call("InputBox", ["Nome:"], runtime)
        self.assertEqual(result, "Maria")
        self.assertEqual(prompts, ["Nome:"])

    def test_inputbox_without_prompt(self) -> None:
        runtime = Runtime(input_provider=lambda _prompt: "42")
        self.assertEqual(self.registry.call("InputBox", [], runtime), "42")

    def test_string_slicing_builtins(self) -> None:
        self.assertEqual(self.registry.call("SubStr", ["ADVPL", 2, 3], self.runtime), "DVP")
        self.assertEqual(self.registry.call("SubStr", ["ADVPL", 3], self.runtime), "VPL")
        self.assertEqual(self.registry.call("Left", ["Python", 3], self.runtime), "Pyt")
        self.assertEqual(self.registry.call("Right", ["Python", 2], self.runtime), "on")

    def test_empty_reports_blank_values(self) -> None:
        self.assertTrue(self.registry.call("Empty", [""], self.runtime))
        self.assertTrue(self.registry.call("Empty", [0], self.runtime))
        self.assertTrue(self.registry.call("Empty", [None], self.runtime))
        self.assertTrue(self.registry.call("Empty", [[]], self.runtime))
        self.assertFalse(self.registry.call("Empty", ["x"], self.runtime))

    def test_numeric_builtins(self) -> None:
        self.assertEqual(self.registry.call("Int", [9.87], self.runtime), 9)
        self.assertEqual(self.registry.call("Round", [3.14159, 2], self.runtime), 3.14)
        self.assertEqual(self.registry.call("Round", [2.5, 0], self.runtime), 3)
        self.assertEqual(self.registry.call("Abs", [-15], self.runtime), 15)

    def test_array_size_builtins(self) -> None:
        values = [1, 2, 3]
        self.assertEqual(self.registry.call("ALen", [values], self.runtime), 3)
        self.registry.call("ASize", [values, 2], self.runtime)
        self.assertEqual(values, [1, 2])

    def test_hash_builtins(self) -> None:
        data: dict = {}
        self.registry.call("HB_HSet", [data, "nome", "Ana"], self.runtime)
        self.assertTrue(self.registry.call("HB_HHasKey", [data, "nome"], self.runtime))
        self.assertEqual(self.registry.call("HB_HGet", [data, "nome"], self.runtime), "Ana")
        self.assertEqual(
            self.registry.call("HB_HGet", [data, "idade", 0], self.runtime), 0
        )


if __name__ == "__main__":
    unittest.main()
