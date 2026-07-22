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
    FUNCTION = auto()  # bare "Function" declaration
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
    CASE = auto()  # "Do Case" branch selector
    OTHERWISE = auto()  # default branch of "Do Case"
    ENDCASE = auto()  # closes a "Do Case" block
    EXIT = auto()
    BREAK = auto()  # leaves the nearest loop, alias of Exit
    LOOP = auto()
    # Object-oriented keywords are recognized by the lexer so the parser can
    # emit a friendly "not yet supported" message instead of a cryptic error.
    CLASS = auto()
    METHOD = auto()
    DATA = auto()
    ENDCLASS = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    CARET = auto()  # exponentiation "^"
    PLUS_PLUS = auto()  # increment "++"
    MINUS_MINUS = auto()  # decrement "--"
    PLUS_ASSIGN = auto()  # "+="
    MINUS_ASSIGN = auto()  # "-="
    STAR_ASSIGN = auto()  # "*="
    SLASH_ASSIGN = auto()  # "/="
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
    COLON = auto()  # member access ":" (reserved for future objects)
    FAT_ARROW = auto()  # hash literal separator "=>"
