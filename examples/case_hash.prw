User Function Menu()

    Local nOpc := 2
    Local hCliente := {"nome" => "Ana", "saldo" => 1500}

    // Objeto simples usando hash e as funcoes HB_H*.
    HB_HSet(hCliente, "ativo", .T.)

    Do Case
        Case nOpc == 1
            ConOut("Cadastro")
        Case nOpc == 2
            ConOut("Cliente: " + hCliente["nome"])
            ConOut("Saldo: " + Str(HB_HGet(hCliente, "saldo")))
        Otherwise
            ConOut("Opcao invalida")
    EndCase

    If HB_HHasKey(hCliente, "ativo")
        ConOut("Status ativo")
    EndIf

Return
