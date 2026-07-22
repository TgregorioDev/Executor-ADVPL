// Valida a cadeia If / ElseIf / Else / EndIf.
User Function TesteElseIf()

    Local nNota := 7

    If nNota >= 9
        ConOut("A")
    ElseIf nNota >= 7
        ConOut("B")
    ElseIf nNota >= 5
        ConOut("C")
    Else
        ConOut("D")
    EndIf

Return
