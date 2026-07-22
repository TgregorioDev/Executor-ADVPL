// Valida funcoes internas numericas e Empty.
User Function TesteBuiltin()

    ConOut(Str(Int(9.87)))
    ConOut(Str(Round(3.14159, 2)))
    ConOut(Str(Abs(-15)))

    If Empty("")
        ConOut("vazio")
    EndIf

    If Empty(0)
        ConOut("zero")
    EndIf

    If !Empty("x")
        ConOut("cheio")
    EndIf

    ConOut(Str(Round(2.5, 0)))

Return
