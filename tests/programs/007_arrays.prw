// Valida arrays: criacao, AAdd, indexacao, alteracao, Len, ALen e ASize.
User Function TesteArrays()

    Local aLista := {}

    AAdd(aLista, 10)
    AAdd(aLista, 20)
    AAdd(aLista, 30)

    aLista[2] := 99

    ConOut(Str(Len(aLista)))
    ConOut(Str(aLista[1]))
    ConOut(Str(aLista[2]))
    ConOut(Str(ALen(aLista)))

    ASize(aLista, 2)
    ConOut(Str(Len(aLista)))

Return
