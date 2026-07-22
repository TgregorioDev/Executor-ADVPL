// Valida funcoes de string e concatenacao.
User Function TesteStrings()

    Local cTexto := "  Mini ADVPL  "

    ConOut(AllTrim(cTexto))
    ConOut(Upper(AllTrim(cTexto)))
    ConOut(Lower("PYTHON"))
    ConOut(Str(Len(AllTrim(cTexto))))
    ConOut(SubStr("ADVPL", 1, 3))
    ConOut(Left("ADVPL", 2))
    ConOut(Right("ADVPL", 2))
    ConOut(Str(Val("42") + 8))
    ConOut("A" + "B" + "C")

Return
