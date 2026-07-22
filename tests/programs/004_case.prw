// Valida o bloco Do Case / Case / Otherwise / EndCase.
User Function TesteCase()

    Local nOpc := 3

    Do Case
        Case nOpc == 1
            ConOut("um")
        Case nOpc == 2
            ConOut("dois")
        Case nOpc == 3
            ConOut("tres")
        Otherwise
            ConOut("outro")
    EndCase

Return
