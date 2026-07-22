import unittest

from src.errors.errors import UnexpectedToken
from src.lexer.lexer import Lexer
from src.parser.ast_nodes import (
    CaseStatement,
    HashLiteral,
    IfStatement,
    IndexAssignment,
    VariableDeclaration,
)
from src.parser.parser import Parser


class ParserTest(unittest.TestCase):
    def parse(self, source: str):
        return Parser(Lexer(source).scan_tokens()).parse()

    def test_parses_do_case_block(self) -> None:
        program = self.parse(
            """
User Function T()
    Do Case
        Case nX == 1
            ConOut("um")
        Otherwise
            ConOut("outro")
    EndCase
Return
"""
        )
        statement = program.functions[0].body[0]
        self.assertIsInstance(statement, CaseStatement)
        self.assertEqual(len(statement.branches), 1)
        self.assertEqual(len(statement.otherwise), 1)

    def test_parses_hash_literal_and_index_assignment(self) -> None:
        program = self.parse(
            """
User Function T()
    Local h := {"a" => 1}
    h["a"] := 2
Return
"""
        )
        body = program.functions[0].body
        self.assertIsInstance(body[0].initializer, HashLiteral)
        self.assertIsInstance(body[1], IndexAssignment)

    def test_error_message_reports_expected_and_position(self) -> None:
        with self.assertRaises(UnexpectedToken) as context:
            self.parse(
                """
User Function T()
    If nX > 1
        ConOut("x")
Return
"""
            )
        message = str(context.exception)
        self.assertIn("Expected EndIf", message)
        self.assertIn("line", message)
        self.assertIn("column", message)

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
