"""Hand-written lexer for the didactic subset of ADVPL.

The lexer is intentionally small and explicit. It converts raw source code into
tokens while keeping line breaks, because ADVPL examples are usually written as
line-oriented programs and the parser can use those breaks as statement
separators.
"""

from src.errors.errors import LexicalError
from src.lexer.token import Token
from src.lexer.token_type import TokenType


class Lexer:
    """Convert ADVPL source code into a list of tokens."""

    KEYWORDS: dict[str, TokenType] = {
        "RETURN": TokenType.RETURN,
        "LOCAL": TokenType.LOCAL,
        "STATIC": TokenType.STATIC,
        "PUBLIC": TokenType.PUBLIC,
        "PRIVATE": TokenType.PRIVATE,
        "IF": TokenType.IF,
        "ELSEIF": TokenType.ELSEIF,
        "ELSE": TokenType.ELSE,
        "ENDIF": TokenType.ENDIF,
        "FOR": TokenType.FOR,
        "TO": TokenType.TO,
        "STEP": TokenType.STEP,
        "NEXT": TokenType.NEXT,
        "DO": TokenType.DO,
        "WHILE": TokenType.WHILE,
        "ENDDO": TokenType.ENDDO,
        "CASE": TokenType.CASE,
        "OTHERWISE": TokenType.OTHERWISE,
        "ENDCASE": TokenType.ENDCASE,
        "EXIT": TokenType.EXIT,
        "BREAK": TokenType.BREAK,
        "LOOP": TokenType.LOOP,
        "FUNCTION": TokenType.FUNCTION,
        "CLASS": TokenType.CLASS,
        "METHOD": TokenType.METHOD,
        "DATA": TokenType.DATA,
        "ENDCLASS": TokenType.ENDCLASS,
        "AND": TokenType.AND,
        "OR": TokenType.OR,
        "NOT": TokenType.NOT,
        "NIL": TokenType.NIL,
        # TRUE/FALSE are accepted as convenience aliases of the .T./.F. logicals.
        "TRUE": TokenType.LOGICAL,
        "FALSE": TokenType.LOGICAL,
    }

    DOTTED_KEYWORDS: dict[str, TokenType] = {
        "AND": TokenType.AND,
        "OR": TokenType.OR,
        "NOT": TokenType.NOT,
    }

    def __init__(self, source: str) -> None:
        self.source = source.replace("\r\n", "\n").replace("\r", "\n")
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_line = 1
        self.start_column = 1

    def scan_tokens(self) -> list[Token]:
        """Tokenize the full source and append an EOF marker."""

        while not self._is_at_end():
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line, self.column))
        return self.tokens

    def _scan_token(self) -> None:
        char = self._advance()

        if char in " \t\f":
            return
        if char == "\n":
            self._add_token(TokenType.NEWLINE)
            return

        if char == "(":
            self._add_token(TokenType.LPAREN)
        elif char == ")":
            self._add_token(TokenType.RPAREN)
        elif char == "[":
            self._add_token(TokenType.LBRACKET)
        elif char == "]":
            self._add_token(TokenType.RBRACKET)
        elif char == "{":
            self._add_token(TokenType.LBRACE)
        elif char == "}":
            self._add_token(TokenType.RBRACE)
        elif char == ",":
            self._add_token(TokenType.COMMA)
        elif char == ";":
            # In this didactic dialect ';' acts as a statement separator, so it
            # is emitted as a NEWLINE and reuses the parser's line handling.
            self._add_token(TokenType.NEWLINE)
        elif char == "+":
            if self._match("="):
                self._add_token(TokenType.PLUS_ASSIGN)
            elif self._match("+"):
                self._add_token(TokenType.PLUS_PLUS)
            else:
                self._add_token(TokenType.PLUS)
        elif char == "-":
            if self._match("="):
                self._add_token(TokenType.MINUS_ASSIGN)
            elif self._match("-"):
                self._add_token(TokenType.MINUS_MINUS)
            else:
                self._add_token(TokenType.MINUS)
        elif char == "*":
            self._add_token(
                TokenType.STAR_ASSIGN if self._match("=") else TokenType.STAR
            )
        elif char == "^":
            self._add_token(TokenType.CARET)
        elif char == "%":
            self._add_token(TokenType.PERCENT)
        elif char == "/":
            self._scan_slash()
        elif char == ":":
            if self._match("="):
                self._add_token(TokenType.ASSIGN)
            else:
                self._add_token(TokenType.COLON)
        elif char == "=":
            if self._match("="):
                self._add_token(TokenType.EQUAL_EQUAL)
            elif self._match(">"):
                self._add_token(TokenType.FAT_ARROW)
            else:
                # A single '=' is treated as equality, matching the executor's
                # existing behavior (assignment uses ':=').
                self._add_token(TokenType.EQUAL_EQUAL)
        elif char == "!":
            # "!=" is inequality; a lone "!" is the logical NOT (e.g. !lAtivo).
            if self._match("="):
                self._add_token(TokenType.NOT_EQUAL)
            else:
                self._add_token(TokenType.NOT)
        elif char == ">":
            self._add_token(
                TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
            )
        elif char == "<":
            if self._match("="):
                self._add_token(TokenType.LESS_EQUAL)
            elif self._match(">"):
                self._add_token(TokenType.NOT_EQUAL)
            else:
                self._add_token(TokenType.LESS)
        elif char in {'"', "'"}:
            self._scan_string(char)
        elif char == ".":
            self._scan_dotted_literal()
        elif char.isdigit():
            self._scan_number()
        elif self._is_identifier_start(char):
            self._scan_identifier()
        else:
            self._fail(f"Unexpected character {char!r}.")

    def _scan_slash(self) -> None:
        if self._match("/"):
            while self._peek() != "\n" and not self._is_at_end():
                self._advance()
            return

        if self._match("*"):
            self._scan_block_comment()
            return

        self._add_token(
            TokenType.SLASH_ASSIGN if self._match("=") else TokenType.SLASH
        )

    def _scan_block_comment(self) -> None:
        while not self._is_at_end():
            if self._peek() == "*" and self._peek_next() == "/":
                self._advance()
                self._advance()
                return
            self._advance()

        self._fail("Unterminated block comment.")

    def _scan_string(self, quote: str) -> None:
        value: list[str] = []

        while not self._is_at_end():
            char = self._advance()

            if char == quote:
                if self._peek() == quote:
                    # xBase strings often escape quotes by doubling them.
                    self._advance()
                    value.append(quote)
                    continue
                self._add_token(TokenType.STRING, "".join(value))
                return

            if char == "\\" and not self._is_at_end():
                value.append(self._read_escape())
                continue

            value.append(char)

        self._fail("Unterminated string literal.")

    def _read_escape(self) -> str:
        escaped = self._advance()
        escapes = {
            "n": "\n",
            "r": "\r",
            "t": "\t",
            '"': '"',
            "'": "'",
            "\\": "\\",
        }
        return escapes.get(escaped, escaped)

    def _scan_number(self) -> None:
        while self._peek().isdigit():
            self._advance()

        is_float = False
        if self._peek() == "." and self._peek_next().isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit():
                self._advance()

        text = self.source[self.start : self.current]
        literal = float(text) if is_float else int(text)
        self._add_token(TokenType.NUMBER, literal)

    def _scan_identifier(self) -> None:
        while self._is_identifier_part(self._peek()):
            self._advance()

        text = self.source[self.start : self.current]
        upper_text = text.upper()

        if upper_text == "USER" and self._consume_following_word("FUNCTION"):
            self._add_token(TokenType.USER_FUNCTION)
            return

        if upper_text == "STATIC" and self._consume_following_word("FUNCTION"):
            self._add_token(TokenType.STATIC_FUNCTION)
            return

        token_type = self.KEYWORDS.get(upper_text, TokenType.IDENTIFIER)

        # TRUE/FALSE map to logical literals, so they carry the boolean value.
        if token_type is TokenType.LOGICAL:
            self._add_token(token_type, upper_text == "TRUE")
            return

        self._add_token(token_type)

    def _scan_dotted_literal(self) -> None:
        closing_dot = self.source.find(".", self.current)
        if closing_dot == -1:
            self._fail("Unterminated dotted literal.")

        text = self.source[self.current : closing_dot].upper()
        if text == "T":
            while self.current <= closing_dot:
                self._advance()
            self._add_token(TokenType.LOGICAL, True)
            return

        if text == "F":
            while self.current <= closing_dot:
                self._advance()
            self._add_token(TokenType.LOGICAL, False)
            return

        token_type = self.DOTTED_KEYWORDS.get(text)
        if token_type is not None:
            while self.current <= closing_dot:
                self._advance()
            self._add_token(token_type)
            return

        self._fail(f"Unsupported dotted literal '.{text}.'.")

    def _consume_following_word(self, word: str) -> bool:
        saved_current = self.current
        saved_column = self.column

        while self._peek() in " \t":
            self._advance()

        end = self.current + len(word)
        candidate = self.source[self.current : end]
        if candidate.upper() == word and not self._is_identifier_part(
            self._char_at(end)
        ):
            while self.current < end:
                self._advance()
            return True

        self.current = saved_current
        self.column = saved_column
        return False

    def _add_token(self, token_type: TokenType, literal: object | None = None) -> None:
        text = self.source[self.start : self.current]
        self.tokens.append(
            Token(token_type, text, literal, self.start_line, self.start_column)
        )

    def _advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self._advance()
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        return self._char_at(self.current + 1)

    def _char_at(self, index: int) -> str:
        if index >= len(self.source):
            return "\0"
        return self.source[index]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _is_identifier_start(self, char: str) -> bool:
        return char == "_" or char.isalpha()

    def _is_identifier_part(self, char: str) -> bool:
        return self._is_identifier_start(char) or char.isdigit()

    def _fail(self, message: str) -> None:
        raise LexicalError(
            f"{message} At line {self.start_line}, column {self.start_column}."
        )
