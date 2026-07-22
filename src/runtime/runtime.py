"""Runtime state: call stack, scopes, functions, input and console output."""

from collections.abc import Callable
from typing import Any

from src.errors.errors import AdvplRuntimeError, UndefinedVariable
from src.parser.ast_nodes import FunctionDeclaration
from src.runtime.scope import Scope
from src.runtime.variables import VariableKind
from src.utils.helpers import normalize_name


class Runtime:
    """Holds mutable execution state for the interpreter."""

    def __init__(
        self,
        input_provider: Callable[[str], str] | None = None,
        output_writer: Callable[[str], None] | None = None,
    ) -> None:
        self.call_stack: list[Scope] = []
        self.static_scope = Scope("static")
        self.public_scope = Scope("public")
        self.private_scope = Scope("private")
        self.functions: dict[str, FunctionDeclaration] = {}
        self.output: list[str] = []
        self.input_provider = input_provider or input
        self.output_writer = output_writer

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
        """Record one console line and, when live, emit it immediately.

        The output list is kept for tests and for callers that inspect the
        console afterwards. When an output_writer is configured (terminal
        execution) the line is also emitted right away, so ConOut interleaves
        correctly with the live prompts printed by InputBox.
        """

        self.output.append(value)
        if self.output_writer is not None:
            self.output_writer(value)

    def read_input(self, prompt: str = "") -> str:
        """Read text from the configured input provider.

        Terminal execution uses Python's input. Tests inject a provider so the
        InputBox built-in is deterministic and never blocks.
        """

        return self.input_provider(prompt)

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
