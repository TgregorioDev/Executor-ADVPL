import unittest

from src.lexer.lexer import Lexer
from src.lexer.token_type import TokenType


class LexerTest(unittest.TestCase):
    def token_types(self, source: str) -> list[TokenType]:
        return [
            token.type
            for token in Lexer(source).scan_tokens()
            if token.type is not TokenType.NEWLINE
        ]

    def test_scans_function_variable_and_if_tokens(self) -> None:
        source = """
User Function Teste()
    Local nIdade := 21
    If nIdade >= 18
        ConOut("Maior")
    EndIf
Return
"""

        self.assertEqual(
            self.token_types(source),
            [
                TokenType.USER_FUNCTION,
                TokenType.IDENTIFIER,
                TokenType.LPAREN,
                TokenType.RPAREN,
                TokenType.LOCAL,
                TokenType.IDENTIFIER,
                TokenType.ASSIGN,
                TokenType.NUMBER,
                TokenType.IF,
                TokenType.IDENTIFIER,
                TokenType.GREATER_EQUAL,
                TokenType.NUMBER,
                TokenType.IDENTIFIER,
                TokenType.LPAREN,
                TokenType.STRING,
                TokenType.RPAREN,
                TokenType.ENDIF,
                TokenType.RETURN,
                TokenType.EOF,
            ],
        )

    def test_ignores_line_and_block_comments(self) -> None:
        tokens = self.token_types(
            """
User Function Comentarios()
    // comentario de linha
    /* comentario
       de bloco */
    ConOut("ok")
Return
"""
        )

        self.assertIn(TokenType.USER_FUNCTION, tokens)
        self.assertIn(TokenType.STRING, tokens)


if __name__ == "__main__":
    unittest.main()
