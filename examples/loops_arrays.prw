User Function LoopsArrays()

    Local aNomes := {}
    Local nI := 0

    AAdd(aNomes, "Ana")
    AAdd(aNomes, "Bruno")
    AAdd(aNomes, "Carla")

    For nI := 1 To Len(aNomes)
        ConOut(Str(nI) + " - " + aNomes[nI])
    Next

Return
