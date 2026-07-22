"""Token value object produced by the lexer and consumed by the parser."""

from dataclasses import dataclass
from typing import Any

from src.lexer.token_type import TokenType


@dataclass(frozen=True)
class Token:
    """Represents one lexical unit and its position in the source file."""

    type: TokenType
    lexeme: str
    literal: Any
    line: int
    column: int

    def location(self) -> str:
        """Return a compact source location for diagnostics."""

        return f"line {self.line}, column {self.column}"
