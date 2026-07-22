// Valida For / Next, atribuicao composta e Step negativo.
User Function TesteFor()

    Local nSoma := 0

    For nI := 1 To 5
        nSoma += nI
    Next

    ConOut(Str(nSoma))

    For nJ := 10 To 2 Step -2
        ConOut(Str(nJ))
    Next

Return
