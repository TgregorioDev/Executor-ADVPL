import unittest

from src.lexer.lexer import Lexer
from src.parser.ast_nodes import IfStatement, VariableDeclaration
from src.parser.parser import Parser


class ParserTest(unittest.TestCase):
    def parse(self, source: str):
        return Parser(Lexer(source).scan_tokens()).parse()

    def test_builds_program_ast(self) -> None:
        program = self.parse(
            """
User Function Teste()
    Local nIdade := 20
    If nIdade >= 18
        ConOut("Maior")
    EndIf
Return
"""
        )

        self.assertEqual(len(program.functions), 1)
        self.assertEqual(program.functions[0].name, "Teste")
        self.assertIsInstance(program.functions[0].body[0], VariableDeclaration)
        self.assertIsInstance(program.functions[0].body[1], IfStatement)

    def test_parses_static_function_after_user_function(self) -> None:
        program = self.parse(
            """
User Function Principal()
    ConOut(Str(Soma(1, 2)))
Return

Static Function Soma(nA, nB)
Return nA + nB
"""
        )

        self.assertEqual([function.name for function in program.functions], ["Principal", "Soma"])


if __name__ == "__main__":
    unittest.main()
