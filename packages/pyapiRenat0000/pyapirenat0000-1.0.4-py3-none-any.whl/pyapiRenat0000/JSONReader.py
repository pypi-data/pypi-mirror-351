import json

class Empty:
    pass

def Read(file: str):
    f = open(file, "r")
    text = f.read()
    try:
        obj = json.load(text)
    except:
        f.close()
        return Empty()
    f.close()
    return obj

def Write(obj: object, file: str):
    f = open(file, "w")
    try:
        text = json.dump(obj)
    except:
        f.close()
        return -1
    f.write(text)
    f.close()
    return 0