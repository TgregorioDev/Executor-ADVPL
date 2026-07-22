"""End-to-end tests that run each learning program in tests/programs/.

Every ``.prw`` file exercises one language feature. The expected console
output is declared here so a regression in any layer (lexer, parser,
interpreter, runtime or built-ins) is caught by a full-program run.
"""

import unittest
from collections.abc import Callable
from pathlib import Path

from src.interpreter.interpreter import Interpreter
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.runtime.runtime import Runtime

PROGRAMS_DIR = Path(__file__).parent / "programs"


def run_program(
    filename: str, input_provider: Callable[[str], str] | None = None
) -> list[str]:
    """Execute one program file and return its simulated console output."""

    source = (PROGRAMS_DIR / filename).read_text(encoding="utf-8")
    tokens = Lexer(source).scan_tokens()
    program = Parser(tokens).parse()
    runtime = Runtime(input_provider=input_provider)
    interpreter = Interpreter(runtime)
    interpreter.interpret(program)
    return runtime.output


def queued_input(values: list[str]) -> Callable[[str], str]:
    """Build an input provider that returns queued answers in order."""

    answers = iter(values)

    def provider(_prompt: str) -> str:
        return next(answers)

    return provider


# Expected output for every program that needs no simulated input.
EXPECTED = {
    "001_variaveis.prw": ["Ana", "30", "100", "ativo", "nulo"],
    "002_if.prw": ["menor"],
    "003_elseif.prw": ["B"],
    "004_case.prw": ["tres"],
    "005_while.prw": ["1", "2", "4", "5"],
    "006_for.prw": ["15", "10", "8", "6", "4", "2"],
    "007_arrays.prw": ["3", "10", "99", "3", "2"],
    "008_funcoes.prw": ["7", "120"],
    "009_strings.prw": [
        "Mini ADVPL",
        "MINI ADVPL",
        "python",
        "10",
        "ADV",
        "AD",
        "PL",
        "50",
        "ABC",
    ],
    "010_operadores.prw": [
        "16", "8", "48", "3", "0", "16", "17", "15", "30", "31", "30",
    ],
    "012_builtin.prw": ["9", "3.14", "15", "vazio", "zero", "cheio", "3"],
    "013_matematica.prw": ["14", "20", "16", "5", "4", "10"],
    "014_comparacoes.prw": [
        "igual",
        "diferente",
        "menor",
        "menorigual",
        "maior",
        "maiorigual",
        "strigual",
    ],
    "015_booleanos.prw": ["and", "or", "not", "true", "bang"],
}


class ProgramsTest(unittest.TestCase):
    def test_all_learning_programs(self) -> None:
        for filename, expected in EXPECTED.items():
            with self.subTest(program=filename):
                self.assertEqual(run_program(filename), expected)

    def test_input_program_reads_values(self) -> None:
        output = run_program(
            "011_input.prw", input_provider=queued_input(["Maria", "20"])
        )
        self.assertEqual(output, ["Ola Maria", "21"])


if __name__ == "__main__":
    unittest.main()
