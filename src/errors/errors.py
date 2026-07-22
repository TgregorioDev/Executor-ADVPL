"""Project-specific exceptions used by the Mini ADVPL pipeline."""


class MiniAdvplError(Exception):
    """Base class for every error raised by the executor."""


class LexicalError(MiniAdvplError):
    """Raised when the lexer finds a character sequence it cannot tokenize."""


class AdvplSyntaxError(MiniAdvplError):
    """Raised when source code does not match the supported grammar."""


class UnexpectedToken(AdvplSyntaxError):
    """Raised when the parser receives a token different from the expected one."""


class UndefinedVariable(MiniAdvplError):
    """Raised when code tries to read or assign a variable that is not visible."""


class DivisionByZero(MiniAdvplError):
    """Raised when a numeric division or modulo receives zero as divisor."""


class TypeMismatch(MiniAdvplError):
    """Raised when an operation receives values of unsupported types."""


class AdvplRuntimeError(MiniAdvplError):
    """Raised for runtime failures not covered by a more specific exception."""


# The prompt asks for a SyntaxError exception. Keeping an alias preserves that
# vocabulary without forcing callers to shadow Python's built-in by default.
SyntaxError = AdvplSyntaxError
