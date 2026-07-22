import unittest

from src.errors.errors import UndefinedVariable
from src.runtime.runtime import Runtime


class VariablesTest(unittest.TestCase):
    def test_local_scope_hides_after_function_leaves(self) -> None:
        runtime = Runtime()
        runtime.enter_function("Teste")
        runtime.declare_variable("LOCAL", "cNome", "Ana")
        self.assertEqual(runtime.read_variable("CNOME"), "Ana")
        runtime.leave_function()

        with self.assertRaises(UndefinedVariable):
            runtime.read_variable("cNome")

    def test_public_scope_survives_between_calls(self) -> None:
        runtime = Runtime()
        runtime.enter_function("A")
        runtime.declare_variable("PUBLIC", "nValor", 10)
        runtime.leave_function()
        runtime.enter_function("B")
        self.assertEqual(runtime.read_variable("nValor"), 10)


if __name__ == "__main__":
    unittest.main()
