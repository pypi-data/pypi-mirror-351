if not __import__("os").path.exists(__import__("sys").prefix+"\\share_variables\\") and __import__("os").path.isdir(__import__("sys").prefix+"\\share_variables"):
    if __import__("os").path.isdir(__import__("sys").prefix+"\\share_variables\\"):
        __import__("os").remove(__import__("sys").prefix+"\\share_variables\\")
    __import__("os").mkdir(__import__("sys").prefix+"\\share_variables\\")

def encrypt_share(name:str,write:bool=True):
    from base64 import b64encode

    assert isinstance(name,str) and isinstance(write,bool)
    
    with open(__import__("sys").prefix+"\\share_variables\\"+name+".json",encoding="u8") as f:
        en=b64encode(("!THIS IS AN ENCRYPTED FILE\n"+f.read()).translate(str.maketrans(
        "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
        "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm"
    )).encode())

    if write:
        with open(__import__("sys").prefix+"\\share_variables\\"+name+".json","w",encoding="u8") as f:
            f.write(en.decode())
    return en

def decrypt_share(name:str,write:bool=False):
    from base64 import b64decode

    assert isinstance(name,str) and isinstance(write,bool)
    with open(__import__("sys").prefix+"\\share_variables\\"+name+".json",encoding="u8") as f:
        de=b64decode(f.read()).decode().translate(str.maketrans(
        "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
        "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm"
    ))

    if write:
        with open(__import__("sys").prefix+"\\share_variables\\"+name+".json","w",encoding="u8") as f:
            f.write(de)
    return de[24:]
