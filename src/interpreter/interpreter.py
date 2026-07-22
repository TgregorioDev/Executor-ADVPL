"""AST interpreter that executes the supported ADVPL subset."""

from datetime import date
from typing import Any

from src.errors.errors import AdvplRuntimeError, DivisionByZero, TypeMismatch
from src.functions.builtin import BuiltinRegistry
from src.lexer.token_type import TokenType
from src.parser.ast_nodes import (
    ArrayLiteral,
    AssignmentStatement,
    BinaryExpression,
    CallExpression,
    CaseStatement,
    Expression,
    ExpressionStatement,
    ExitStatement,
    ForStatement,
    HashLiteral,
    Identifier,
    IfStatement,
    IndexAssignment,
    IndexExpression,
    Literal,
    LoopStatement,
    Program,
    ReturnStatement,
    Statement,
    UnaryExpression,
    VariableDeclaration,
    WhileStatement,
)
from src.runtime.runtime import Runtime
from src.utils.helpers import format_value, is_numeric, is_truthy, normalize_name


class _ReturnSignal(Exception):
    """Internal control-flow signal for Return."""

    def __init__(self, value: Any) -> None:
        self.value = value


class _ExitSignal(Exception):
    """Internal control-flow signal for EXIT."""


class _LoopSignal(Exception):
    """Internal control-flow signal for LOOP."""


class Interpreter:
    """Visit AST nodes and execute the program against a Runtime instance."""

    def __init__(self, runtime: Runtime | None = None) -> None:
        self.runtime = runtime or Runtime()
        self.builtins = BuiltinRegistry()

    def interpret(self, program: Program, entry_point: str | None = None) -> Any:
        """Register functions and execute the chosen entry point."""

        if not program.functions:
            raise AdvplRuntimeError("Program does not declare any function.")

        for function in program.functions:
            self.runtime.register_function(function)

        entry_name = entry_point or self._default_entry_point(program)
        return self._call_user_function(entry_name, [])

    def visit_VariableDeclaration(self, node: VariableDeclaration) -> None:
        value = self._evaluate(node.initializer) if node.initializer else None
        self.runtime.declare_variable(node.kind, node.name, value)
        return None

    def visit_AssignmentStatement(self, node: AssignmentStatement) -> None:
        self.runtime.assign_variable(node.name, self._evaluate(node.value))
        return None

    def visit_IndexAssignment(self, node: IndexAssignment) -> None:
        collection = self._evaluate(node.collection)
        value = self._evaluate(node.value)

        if isinstance(collection, dict):
            # Hashes (simple objects) are keyed by the raw value.
            collection[self._evaluate(node.index)] = value
            return None

        if isinstance(collection, list):
            index = self._number(self._evaluate(node.index), "array index")
            if not float(index).is_integer():
                raise TypeMismatch("Array index must be an integer.")
            zero_based = int(index) - 1
            try:
                collection[zero_based] = value
            except IndexError as exc:
                raise AdvplRuntimeError("Array index out of range.") from exc
            return None

        raise TypeMismatch("Element assignment expects an array or a hash.")

    def visit_IfStatement(self, node: IfStatement) -> None:
        if is_truthy(self._evaluate(node.condition)):
            self._execute_block(node.then_branch)
            return None

        for condition, statements in node.elseif_branches:
            if is_truthy(self._evaluate(condition)):
                self._execute_block(statements)
                return None

        self._execute_block(node.else_branch)
        return None

    def visit_CaseStatement(self, node: CaseStatement) -> None:
        # Execute the first branch whose condition is truthy, mirroring the
        # top-to-bottom evaluation of ADVPL's Do Case block.
        for condition, statements in node.branches:
            if is_truthy(self._evaluate(condition)):
                self._execute_block(statements)
                return None

        self._execute_block(node.otherwise)
        return None

    def visit_ForStatement(self, node: ForStatement) -> None:
        start = self._number(self._evaluate(node.start), "FOR start")
        end = self._number(self._evaluate(node.end), "FOR end")
        step = self._number(self._evaluate(node.step), "FOR step") if node.step else 1

        if step == 0:
            raise TypeMismatch("FOR step cannot be zero.")

        current = start
        self.runtime.assign_or_declare_local(node.variable, current)

        while self._for_should_continue(current, end, step):
            try:
                self._execute_block(node.body)
            except _LoopSignal:
                pass
            except _ExitSignal:
                break

            current = self._number(self.runtime.read_variable(node.variable), "FOR")
            current += step
            self.runtime.assign_variable(node.variable, current)

        return None

    def visit_WhileStatement(self, node: WhileStatement) -> None:
        while is_truthy(self._evaluate(node.condition)):
            try:
                self._execute_block(node.body)
            except _LoopSignal:
                continue
            except _ExitSignal:
                break
        return None

    def visit_ExitStatement(self, _node: ExitStatement) -> None:
        raise _ExitSignal()

    def visit_LoopStatement(self, _node: LoopStatement) -> None:
        raise _LoopSignal()

    def visit_ReturnStatement(self, node: ReturnStatement) -> None:
        value = self._evaluate(node.value) if node.value else None
        raise _ReturnSignal(value)

    def visit_ExpressionStatement(self, node: ExpressionStatement) -> Any:
        return self._evaluate(node.expression)

    def visit_Literal(self, node: Literal) -> Any:
        return node.value

    def visit_Identifier(self, node: Identifier) -> Any:
        return self.runtime.read_variable(node.name)

    def visit_UnaryExpression(self, node: UnaryExpression) -> Any:
        operand = self._evaluate(node.operand)

        if node.operator is TokenType.NOT:
            return not is_truthy(operand)
        if node.operator is TokenType.MINUS:
            return -self._number(operand, "unary '-'")
        if node.operator is TokenType.PLUS:
            return self._number(operand, "unary '+'")

        raise AdvplRuntimeError(f"Unsupported unary operator {node.operator.name}.")

    def visit_BinaryExpression(self, node: BinaryExpression) -> Any:
        if node.operator is TokenType.OR:
            return is_truthy(self._evaluate(node.left)) or is_truthy(
                self._evaluate(node.right)
            )
        if node.operator is TokenType.AND:
            return is_truthy(self._evaluate(node.left)) and is_truthy(
                self._evaluate(node.right)
            )

        left = self._evaluate(node.left)
        right = self._evaluate(node.right)

        if node.operator is TokenType.PLUS:
            return self._plus(left, right)
        if node.operator is TokenType.MINUS:
            return self._number(left, "-") - self._number(right, "-")
        if node.operator is TokenType.STAR:
            return self._number(left, "*") * self._number(right, "*")
        if node.operator is TokenType.SLASH:
            divisor = self._number(right, "/")
            if divisor == 0:
                raise DivisionByZero("Division by zero.")
            return self._number(left, "/") / divisor
        if node.operator is TokenType.PERCENT:
            divisor = self._number(right, "%")
            if divisor == 0:
                raise DivisionByZero("Modulo by zero.")
            return self._number(left, "%") % divisor
        if node.operator is TokenType.CARET:
            return self._number(left, "^") ** self._number(right, "^")
        if node.operator is TokenType.EQUAL_EQUAL:
            return left == right
        if node.operator is TokenType.NOT_EQUAL:
            return left != right
        if node.operator in {
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        }:
            return self._compare(left, node.operator, right)

        raise AdvplRuntimeError(f"Unsupported binary operator {node.operator.name}.")

    def visit_CallExpression(self, node: CallExpression) -> Any:
        if not isinstance(node.callee, Identifier):
            raise TypeMismatch("Only named function calls are supported.")

        name = node.callee.name
        arguments = [self._evaluate(argument) for argument in node.arguments]

        if self.builtins.has(name):
            return self.builtins.call(name, arguments, self.runtime)

        return self._call_user_function(name, arguments)

    def visit_ArrayLiteral(self, node: ArrayLiteral) -> list[Any]:
        return [self._evaluate(element) for element in node.elements]

    def visit_HashLiteral(self, node: HashLiteral) -> dict[Any, Any]:
        # A hash literal builds a Python dict, the didactic "simple object".
        return {
            self._evaluate(key): self._evaluate(value) for key, value in node.pairs
        }

    def visit_IndexExpression(self, node: IndexExpression) -> Any:
        collection = self._evaluate(node.collection)

        # Hashes are accessed by key, arrays and strings by 1-based position.
        if isinstance(collection, dict):
            key = self._evaluate(node.index)
            if key not in collection:
                raise AdvplRuntimeError(f"Hash key {key!r} not found.")
            return collection[key]

        index = self._number(self._evaluate(node.index), "array index")
        if not float(index).is_integer():
            raise TypeMismatch("Array index must be an integer.")

        zero_based = int(index) - 1
        if isinstance(collection, (list, str)):
            try:
                return collection[zero_based]
            except IndexError as exc:
                raise AdvplRuntimeError("Array index out of range.") from exc

        raise TypeMismatch("Indexing is supported only for arrays, strings and hashes.")

    def _default_entry_point(self, program: Program) -> str:
        for function in program.functions:
            if function.kind == "USER":
                return function.name
        return program.functions[0].name

    def _call_user_function(self, name: str, arguments: list[Any]) -> Any:
        function = self.runtime.get_function(name)
        if function is None:
            raise AdvplRuntimeError(f"Undefined function '{name}'.")

        if len(arguments) != len(function.params):
            raise TypeMismatch(
                f"{function.name} expects {len(function.params)} arguments, "
                f"got {len(arguments)}."
            )

        self.runtime.enter_function(function.name)
        try:
            for param, argument in zip(function.params, arguments):
                self.runtime.declare_variable("LOCAL", param, argument)
            self._execute_block(function.body)
        except _ReturnSignal as signal:
            return signal.value
        finally:
            self.runtime.leave_function()

        return None

    def _execute_block(self, statements: list[Statement]) -> None:
        for statement in statements:
            statement.accept(self)

    def _evaluate(self, expression: Expression | None) -> Any:
        if expression is None:
            return None
        return expression.accept(self)

    def _plus(self, left: Any, right: Any) -> Any:
        if is_numeric(left) and is_numeric(right):
            return left + right
        if isinstance(left, str) or isinstance(right, str):
            return format_value(left) + format_value(right)
        raise TypeMismatch("Operator '+' expects numbers or strings.")

    def _compare(self, left: Any, operator: TokenType, right: Any) -> bool:
        if is_numeric(left) and is_numeric(right):
            return self._compare_values(left, operator, right)
        if isinstance(left, str) and isinstance(right, str):
            return self._compare_values(left, operator, right)
        if isinstance(left, date) and isinstance(right, date):
            return self._compare_values(left, operator, right)
        raise TypeMismatch("Comparison expects values of compatible types.")

    def _compare_values(self, left: Any, operator: TokenType, right: Any) -> bool:
        if operator is TokenType.GREATER:
            return left > right
        if operator is TokenType.GREATER_EQUAL:
            return left >= right
        if operator is TokenType.LESS:
            return left < right
        if operator is TokenType.LESS_EQUAL:
            return left <= right
        raise AdvplRuntimeError(f"Unsupported comparison {operator.name}.")

    def _number(self, value: Any, context: str) -> int | float:
        if is_numeric(value):
            return value
        raise TypeMismatch(f"{context} expects a numeric value.")

    def _for_should_continue(
        self, current: int | float, end: int | float, step: int | float
    ) -> bool:
        if step > 0:
            return current <= end
        return current >= end



