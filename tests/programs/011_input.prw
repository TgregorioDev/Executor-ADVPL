// Valida a leitura de dados via InputBox (simulada nos testes).
User Function TesteInput()

    Local cNome := InputBox("Nome:")
    ConOut("Ola " + cNome)

    Local nIdade := Val(InputBox("Idade:"))
    ConOut(Str(nIdade + 1))

Return
