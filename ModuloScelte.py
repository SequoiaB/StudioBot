def getSubject(data):
    try:
        subject= ""
        if data == 0:
            subject = "Telecomunicazioni"
        elif data == 1:
            subject = "IS"
        elif data == 2:
            subject = "AxI"
        elif data == 3:
            subject = "Automazione Industriale"
        #if data == 6:
        #    subject = "boh"
        return subject
    except Exception as e:
        print("errore in getSubject", e)
        return "error"
    
def getStudyTime(data):
    try:
        studio = 0
        if data == 0:
            studio = 20
        elif data == 1:
            studio = 25
        elif data == 2:
            studio = 30
        elif data == 3:
            studio = 35
        elif data == 4:
            studio = 40
        elif data == 5:
            studio = 45
        elif data == 6:
            studio = 50
        elif data == 7:
            studio = 55
        elif data == 8:
            studio = 60

        return studio
    except Exception as e:
        print("errore in getStudyTime", e)
        return "error"
    
def getPauseTime(data):
    try:
        pausa = 0
        if data == 0:
            pausa = 5
        elif data == 1:
            pausa = 7
        elif data == 2:
            pausa = 9
        elif data == 3:
            pausa = 10
        elif data == 4:
            pausa = 12
        elif data == 5:
            pausa = 14
        elif data == 6:
            pausa = 15
        elif data == 7:
            pausa = 17
        elif data == 8:
            pausa = 20
            
        return pausa
    except Exception as e:
        print("errore in getStudyTime", e)
        return "error"