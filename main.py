"""Command-line entry point for the Mini ADVPL executor."""

from pathlib import Path
import sys

from src.errors.errors import MiniAdvplError
from src.interpreter.interpreter import Interpreter
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.runtime.runtime import Runtime


def _print_line(line: str) -> None:
    """Emit a console line live so ConOut interleaves with InputBox prompts."""

    print(line, flush=True)


def execute_file(path: Path) -> list[str]:
    """Execute an ADVPL source file, printing console output live."""

    source = path.read_text(encoding="utf-8")
    tokens = Lexer(source).scan_tokens()
    program = Parser(tokens).parse()
    interpreter = Interpreter(Runtime(output_writer=_print_line))
    interpreter.interpret(program)
    return interpreter.runtime.output


def main(argv: list[str]) -> int:
    """Run the CLI interface."""

    if len(argv) != 2:
        print("Usage: python main.py arquivo.prw", file=sys.stderr)
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    try:
        execute_file(path)
    except MiniAdvplError as exc:
        print(f"Mini ADVPL error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
