// Valida operadores aritmeticos, potencia e atribuicoes compostas.
User Function TesteOperadores()

    Local nA := 12
    Local nB := 4

    ConOut(Str(nA + nB))
    ConOut(Str(nA - nB))
    ConOut(Str(nA * nB))
    ConOut(Str(nA / nB))
    ConOut(Str(nA % nB))
    ConOut(Str(2 ^ 4))

    nA += 5
    ConOut(Str(nA))
    nA -= 2
    ConOut(Str(nA))
    nA *= 2
    ConOut(Str(nA))
    nA++
    ConOut(Str(nA))
    nA--
    ConOut(Str(nA))

Return
