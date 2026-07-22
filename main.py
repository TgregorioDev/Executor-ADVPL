"""Command-line entry point for the Mini ADVPL executor."""

from pathlib import Path
import sys

from src.errors.errors import MiniAdvplError
from src.interpreter.interpreter import Interpreter
from src.lexer.lexer import Lexer
from src.parser.parser import Parser


def execute_file(path: Path) -> list[str]:
    """Execute an ADVPL source file and return simulated console output."""

    source = path.read_text(encoding="utf-8")
    tokens = Lexer(source).scan_tokens()
    program = Parser(tokens).parse()
    interpreter = Interpreter()
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
        for line in execute_file(path):
            print(line)
    except MiniAdvplError as exc:
        print(f"Mini ADVPL error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
