// Valida declaracao de variaveis Local e Public, tipos basicos e Nil.
User Function Variaveis()

    Local cNome := "Ana"
    Local nIdade := 30
    Local lAtivo := .T.
    Local xNulo := NIL
    Public nContador := 100

    ConOut(cNome)
    ConOut(Str(nIdade))
    ConOut(Str(nContador))

    If lAtivo
        ConOut("ativo")
    EndIf

    If Empty(xNulo)
        ConOut("nulo")
    EndIf

Return
