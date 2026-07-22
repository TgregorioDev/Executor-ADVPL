"""Token kinds recognized by the hand-written ADVPL lexer."""

from enum import Enum, auto


class TokenType(Enum):
    """All lexical symbols understood by the first interpreter version."""

    EOF = auto()
    NEWLINE = auto()

    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    LOGICAL = auto()
    NIL = auto()

    USER_FUNCTION = auto()
    STATIC_FUNCTION = auto()
    RETURN = auto()
    LOCAL = auto()
    STATIC = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    IF = auto()
    ELSEIF = auto()
    ELSE = auto()
    ENDIF = auto()
    FOR = auto()
    TO = auto()
    STEP = auto()
    NEXT = auto()
    DO = auto()
    WHILE = auto()
    ENDDO = auto()
    EXIT = auto()
    LOOP = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQUAL_EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
