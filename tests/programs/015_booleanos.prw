// Valida operadores booleanos AND/OR/NOT e os literais logicos.
User Function TesteBooleanos()

    Local lA := .T.
    Local lB := .F.

    If lA AND NOT lB
        ConOut("and")
    EndIf

    If lB OR lA
        ConOut("or")
    EndIf

    If NOT lB
        ConOut("not")
    EndIf

    If TRUE
        ConOut("true")
    EndIf

    If !FALSE
        ConOut("bang")
    EndIf

Return
