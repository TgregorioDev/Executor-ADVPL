"""Runtime state: call stack, scopes, functions and console output."""

from typing import Any

from src.errors.errors import AdvplRuntimeError, UndefinedVariable
from src.parser.ast_nodes import FunctionDeclaration
from src.runtime.scope import Scope
from src.runtime.variables import VariableKind
from src.utils.helpers import normalize_name


class Runtime:
    """Holds mutable execution state for the interpreter."""

    def __init__(self) -> None:
        self.call_stack: list[Scope] = []
        self.static_scope = Scope("static")
        self.public_scope = Scope("public")
        self.private_scope = Scope("private")
        self.functions: dict[str, FunctionDeclaration] = {}
        self.output: list[str] = []

    def register_function(self, function: FunctionDeclaration) -> None:
        """Register a function using ADVPL's case-insensitive naming model."""

        self.functions[normalize_name(function.name)] = function

    def get_function(self, name: str) -> FunctionDeclaration | None:
        """Find a user-defined function by name."""

        return self.functions.get(normalize_name(name))

    def enter_function(self, name: str) -> None:
        """Push a local scope for a function invocation."""

        self.call_stack.append(Scope(name))

    def leave_function(self) -> None:
        """Pop the current local function scope."""

        if not self.call_stack:
            raise AdvplRuntimeError("Cannot leave function: call stack is empty.")
        self.call_stack.pop()

    def declare_variable(self, kind_name: str, name: str, value: Any) -> None:
        """Declare a variable according to the simplified ADVPL scope rules."""

        kind = VariableKind[kind_name]
        self._scope_for(kind).define(name, kind, value)

    def read_variable(self, name: str) -> Any:
        """Resolve a variable using local, private, static and public scopes."""

        scope = self._find_scope_containing(name)
        if scope is None:
            raise UndefinedVariable(f"Undefined variable '{name}'.")
        return scope.get(name)

    def assign_variable(self, name: str, value: Any) -> None:
        """Assign the nearest visible variable with this name."""

        scope = self._find_scope_containing(name)
        if scope is None:
            raise UndefinedVariable(f"Undefined variable '{name}'.")
        scope.assign(name, value)

    def assign_or_declare_local(self, name: str, value: Any) -> None:
        """Assign a loop variable or create it as LOCAL when absent.

        ADVPL examples often show FOR variables without a separate declaration.
        The executor accepts that as a beginner-friendly shortcut.
        """

        scope = self._find_scope_containing(name)
        if scope is None:
            self.declare_variable("LOCAL", name, value)
            return
        scope.assign(name, value)

    def write_output(self, value: str) -> None:
        """Append one line to the simulated console output."""

        self.output.append(value)

    @property
    def current_scope(self) -> Scope:
        """Return the local scope at the top of the call stack."""

        if not self.call_stack:
            raise AdvplRuntimeError("No active function scope.")
        return self.call_stack[-1]

    def _scope_for(self, kind: VariableKind) -> Scope:
        if kind is VariableKind.LOCAL:
            return self.current_scope
        if kind is VariableKind.STATIC:
            return self.static_scope
        if kind is VariableKind.PUBLIC:
            return self.public_scope
        if kind is VariableKind.PRIVATE:
            return self.private_scope
        raise AdvplRuntimeError(f"Unsupported variable kind {kind.value}.")

    def _find_scope_containing(self, name: str) -> Scope | None:
        for scope in reversed(self.call_stack):
            if scope.contains(name):
                return scope

        for scope in (self.private_scope, self.static_scope, self.public_scope):
            if scope.contains(name):
                return scope

        return None
