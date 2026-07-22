"""Abstract syntax tree nodes for the supported ADVPL subset."""

from dataclasses import dataclass, field
from typing import Any, Protocol

from src.lexer.token_type import TokenType


class Visitor(Protocol):
    """Protocol implemented by AST visitors such as the interpreter."""


class Node:
    """Base AST node with dynamic visitor dispatch."""

    def accept(self, visitor: Visitor) -> Any:
        """Call the visitor method dedicated to this concrete node."""

        method_name = f"visit_{self.__class__.__name__}"
        method = getattr(visitor, method_name)
        return method(self)


class Statement(Node):
    """Base class for executable statements."""


class Expression(Node):
    """Base class for expressions that produce values."""


@dataclass
class Program(Node):
    """Root node containing all function declarations found in the file."""

    functions: list["FunctionDeclaration"]


@dataclass
class FunctionDeclaration(Node):
    """Represents a User Function or Static Function block."""

    kind: str
    name: str
    params: list[str]
    body: list[Statement] = field(default_factory=list)


@dataclass
class VariableDeclaration(Statement):
    """Represents LOCAL, STATIC, PUBLIC and PRIVATE declarations."""

    kind: str
    name: str
    initializer: Expression | None


@dataclass
class AssignmentStatement(Statement):
    """Represents assignment to an already visible variable."""

    name: str
    value: Expression


@dataclass
class IndexAssignment(Statement):
    """Represents assignment to an array or hash element (``a[i] := v``)."""

    collection: Expression
    index: Expression
    value: Expression


@dataclass
class IfStatement(Statement):
    """Represents IF / ELSEIF / ELSE / ENDIF control flow."""

    condition: Expression
    then_branch: list[Statement]
    elseif_branches: list[tuple[Expression, list[Statement]]]
    else_branch: list[Statement]


@dataclass
class ForStatement(Statement):
    """Represents a FOR / NEXT loop with optional STEP."""

    variable: str
    start: Expression
    end: Expression
    step: Expression | None
    body: list[Statement]


@dataclass
class WhileStatement(Statement):
    """Represents a DO WHILE / ENDDO loop."""

    condition: Expression
    body: list[Statement]


@dataclass
class CaseStatement(Statement):
    """Represents a DO CASE / CASE / OTHERWISE / ENDCASE selection block."""

    branches: list[tuple[Expression, list[Statement]]]
    otherwise: list[Statement]


@dataclass
class ExitStatement(Statement):
    """Represents EXIT, which leaves the nearest loop."""


@dataclass
class LoopStatement(Statement):
    """Represents LOOP, which jumps to the next loop iteration."""


@dataclass
class ReturnStatement(Statement):
    """Represents Return with an optional value."""

    value: Expression | None


@dataclass
class ExpressionStatement(Statement):
    """Wraps an expression used as a statement, commonly a function call."""

    expression: Expression


@dataclass
class Literal(Expression):
    """Represents literal values: strings, numbers, logicals and Nil."""

    value: Any


@dataclass
class Identifier(Expression):
    """Represents a variable or function name."""

    name: str


@dataclass
class UnaryExpression(Expression):
    """Represents unary operators such as NOT and negative numbers."""

    operator: TokenType
    operand: Expression


@dataclass
class BinaryExpression(Expression):
    """Represents infix operators with precedence handled by the parser."""

    left: Expression
    operator: TokenType
    right: Expression


@dataclass
class CallExpression(Expression):
    """Represents a function call expression."""

    callee: Expression
    arguments: list[Expression]


@dataclass
class ArrayLiteral(Expression):
    """Represents an ADVPL-style array literal such as {1, 2, 3}."""

    elements: list[Expression]


@dataclass
class HashLiteral(Expression):
    """Represents a hash literal such as {"nome" => "Ana", "idade" => 30}.

    Hashes are the didactic stand-in for "simple objects" in this executor.
    """

    pairs: list[tuple[Expression, Expression]]


@dataclass
class IndexExpression(Expression):
    """Represents 1-based indexing into arrays or strings."""

    collection: Expression
    index: Expression
