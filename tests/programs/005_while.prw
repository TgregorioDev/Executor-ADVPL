// Valida Do While / EndDo com os controles Loop e Exit.
User Function TesteWhile()

    Local nI := 0

    Do While nI < 10
        nI++
        If nI == 3
            Loop
        EndIf
        If nI == 6
            Exit
        EndIf
        ConOut(Str(nI))
    EndDo

Return
