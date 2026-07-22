import unittest

from src.interpreter.interpreter import Interpreter
from src.lexer.lexer import Lexer
from src.parser.parser import Parser


def run_advpl(source: str) -> list[str]:
    tokens = Lexer(source).scan_tokens()
    program = Parser(tokens).parse()
    interpreter = Interpreter()
    interpreter.interpret(program)
    return interpreter.runtime.output


class InterpreterTest(unittest.TestCase):
    def test_runs_hello_world(self) -> None:
        self.assertEqual(
            run_advpl(
                """
User Function Ola()
    ConOut("Ola Mundo")
Return
"""
            ),
            ["Ola Mundo"],
        )

    def test_runs_variables_and_builtins(self) -> None:
        self.assertEqual(
            run_advpl(
                """
User Function Texto()
    Local cNome := "  maria  "
    ConOut(Upper(AllTrim(cNome)))
    ConOut(Str(Val("42") + 8))
Return
"""
            ),
            ["MARIA", "50"],
        )

    def test_runs_if_else(self) -> None:
        self.assertEqual(
            run_advpl(
                """
User Function Teste()
    Local nIdade := 17
    If nIdade >= 18
        ConOut("Maior")
    Else
        ConOut("Menor")
    EndIf
Return
"""
            ),
            ["Menor"],
        )

    def test_runs_for_loop(self) -> None:
        self.assertEqual(
            run_advpl(
                """
User Function SomaFor()
    Local nTotal := 0
    For nI := 1 To 3
        nTotal := nTotal + nI
    Next
    ConOut(Str(nTotal))
Return
"""
            ),
            ["6"],
        )

    def test_runs_while_loop(self) -> None:
        self.assertEqual(
            run_advpl(
                """
User Function Enquanto()
    Local nI := 0
    Do While nI < 3
        nI := nI + 1
        ConOut(Str(nI))
    EndDo
Return
"""
            ),
            ["1", "2", "3"],
        )

    def test_runs_functions_with_return_values(self) -> None:
        self.assertEqual(
            run_advpl(
                """
User Function Principal()
    ConOut(Str(Soma(10, 5)))
Return

Static Function Soma(nA, nB)
Return nA + nB
"""
            ),
            ["15"],
        )

    def test_runs_arrays_aadd_len_and_indexing(self) -> None:
        self.assertEqual(
            run_advpl(
                """
User Function Arrays()
    Local aItens := {}
    AAdd(aItens, "ADVPL")
    AAdd(aItens, "Python")
    ConOut(Str(Len(aItens)))
    ConOut(aItens[2])
Return
"""
            ),
            ["2", "Python"],
        )

    def test_runs_logical_elseif_and_dates(self) -> None:
        self.assertEqual(
            run_advpl(
                """
User Function Datas()
    Local dHoje := CToD("22/07/2026")
    Local dInicio := CToD("01/01/2026")
    Local lAtivo := .T.

    If lAtivo AND dHoje > dInicio
        ConOut(DToC(dHoje))
    ElseIf NOT lAtivo
        ConOut("inativo")
    Else
        ConOut("sem data")
    EndIf
Return
"""
            ),
            ["22/07/2026"],
        )
    def test_exit_and_loop_control_loops(self) -> None:
        self.assertEqual(
            run_advpl(
                """
User Function Controle()
    For nI := 1 To 5
        If nI == 2
            Loop
        EndIf
        If nI == 4
            Exit
        EndIf
        ConOut(Str(nI))
    Next
Return
"""
            ),
            ["1", "3"],
        )


if __name__ == "__main__":
    unittest.main()


