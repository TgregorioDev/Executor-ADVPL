User Function Datas()

    Local dHoje := CToD("22/07/2026")
    Local dInicio := CToD("01/01/2026")

    If dHoje > dInicio
        ConOut("Data atual: " + DToC(dHoje))
    EndIf

Return
