// Valida funcoes: parametros, retorno, chamadas entre funcoes e recursao.
User Function TesteFuncoes()

    ConOut(Str(Soma(3, 4)))
    ConOut(Str(Fatorial(5)))

Return

Static Function Soma(nA, nB)
Return nA + nB

Static Function Fatorial(nN)
    If nN <= 1
        Return 1
    EndIf
Return nN * Fatorial(nN - 1)
