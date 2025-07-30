from . import operators

juris = {}
player_level = {}

LEVEL = "level"
JURIS_NAME = "juris"
PLAYER_NAME = "player"
if not __import__("os").path.exists(__import__("sys").prefix+"\\juris") and __import__("os").path.isdir(__import__("sys").prefix+"\\juris"):
    if __import__("os").path.isdir(__import__("sys").prefix+"\\juris"):
        __import__("os").remove(__import__("sys").prefix+"\\juris")
    __import__("os").mkdir(__import__("sys").prefix+"\\juris")

def append(**kwargs):
    """Add the juris to juris,if juris in juris,set the juris."""
    for k,v in kwargs.items():
        juris[k] = v

def get(key:str = None)->dict:
    """get the keys juris,if keys is none,return the juris list,else return the key juris`s value."""
    assert isinstance(key,str)
    try:
        return juris[key]
    except:
        raise NameError(key+" is not in juris.")

def set(**kwargs):
    """Same as and."""
    for k,v in kwargs.items():
        juris[k] = v

def judge(jurises,level):
    assert isinstance(level,int) and isinstance(juris,str)
    try:
        return juris[jurises] == level
    except Exception as e:
        raise NameError(e)
    
def juris_in_list(type,judge):
    assert isinstance(type,str) and (isinstance(judge,str) or isinstance(judge,int))
    if type == LEVEL:
        for k,v in juris.items():
            if v == judge:
                return True
        return False
    elif type ==  JURIS_NAME:
        return judge in juris
    else:
        raise NameError(type+" is not in temp.")

def getPlayer(key:str = None)->dict:
    """get the player juris"""
    assert isinstance(key,str)
    try:
        return juris[key]
    except:
        raise NameError(key+" is not in juris.")
    
def changePlayer(func,num,key:str = None)->dict:
    """get the player juris"""
    assert isinstance(key,str)
    try:
        juris[key] = func(juris[key],num)
        return juris[key]
    except:
        raise NameError(key+" is not in juris.")
    
def delPlayer(key:str):
    """delete the player keys."""
    assert isinstance(key,str)
    try:
        del player_level[key]
    except:
        raise NameError(key+" is not in juris.")

def setPlayer(**kwargs):
    """Set the player Level"""
    for k,v in kwargs.items():
        assert juris_in_list(JURIS_NAME,k)
        player_level[k] = v

def player_judge(type,judge):
    assert isinstance(type,str) and (isinstance(judge,str) or isinstance(judge,int))
    if type == LEVEL:
        for k,v in player_level.items():
            if juris[k] == judge:
                return True
        return False
    elif type ==  PLAYER_NAME:
        return judge in player_level
    else:
        raise NameError(type+" is not in temp.")
    
def download(name,output:bool = False):
    from base64 import b64decode
    try:
        with open(__import__("sys").prefix+"\\juris"+"\\"+name+".json",encoding = "u8") as f:
            file = f.read()
        index = 0
        for i in "IUdVVkYgVkYgTkEgUkFQRUxDR1JRIFNWWVIKe":
            if file[index] != i:
                if output:
                    print("already download '"+name+"' to'"+__import__("sys").prefix+"\\juris"+"\\"+name+".json")
                return file
            index+= 1
        if output:
            print("already download '"+name+"' to'"+__import__("sys").prefix+"\\juris"+"\\"+name+".json")
        return (b64decode(file).decode())[24:].translate(str.maketrans(
        "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
        "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm"
        ))
    except Exception as e:
        if output:
            print(e)
        else:
            raise Exception(e)

def upload(name,encrypted:bool = False,output:bool = False):
    try:
        from base64 import b64encode
        if encrypted:
            with open(__import__("sys").prefix+"\\juris"+"\\"+name+".json","w",encoding = "u8") as f:
                print(str(juris).replace("'",'"'))
                en = b64encode(("!THIS IS AN ENCRYPTED FILE\n"+str(juris).replace("'",'"')).translate(str.maketrans(
                    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
                    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm"
                )).encode()).decode()
                f.write(en)
                if output:
                    print("already upload '"+name+"' to'"+__import__("sys").prefix+"\\juris"+"\\"+name+".json")
                return en
        else:
            with open(__import__("sys").prefix+"\\juris"+"\\"+name+".json","w",encoding = "u8") as f:
                en = str(juris).replace("'",'"')
                f.write(en)
                if output:
                    print("already upload '"+name+"' to'"+__import__("sys").prefix+"\\juris"+"\\"+name+".json")
                return en 
    except Exception as e:
        if output:
            print(e)
        else:
            raise Exception(e)
        
class User:
    def __init__(self,name,level):
        self.name = name
        self.level = level
    
    def change(self,do,value):
        self.level = do(self.level,value)
        return self

    def operator(self,do,value):
        if isinstance(value,User):
            return do(self.level,value.level)
        elif isinstance(value,int):
            return do(self.level,value)
        else:
            raise TypeError("value '"+str(value)+"' is"+str(type(value))+",not User or int.")
    
    def __eq__(self,value :int):
        return self.operator(operators.comparison.eq,value)

    def __ne__(self,value :int):
        return self.operator(operators.comparison.ne,value)

    def __lt__(self,value :int):
        return self.operator(operators.comparison.lt,value)

    def __gt__(self,value :int):
        return self.operator(operators.comparison.gt,value)

    def __le__(self,value :int):
        return self.operator(operators.comparison.le,value)

    def __ge__(self,value :int):    
        return self.operator(operators.comparison.ge,value)
    
    def __add__(self,value :int):
        return self.change(operators.matical.add,value)

    def __sub__(self,value :int):
        return self.change(operators.matical.sub,value)
    
    def __radd__(self,value :int):
        return self.change(operators.matical.add,value)

    def __rsub__(self,value :int):
        return self.change(operators.matical.sub,value)
    
    def __lshift__(self,value):
        return self.change(operators.matical.sub,value)
        
    def __rlshift__(self,value):
        return self.change(operators.matical.sub,value)

    def __rshift__(self,value):
        return self.change(operators.matical.add,value)
        
    def __rrshift__(self,value):
        return self.change(operators.matical.add,value)
