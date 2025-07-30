from . import encrypt

if not __import__("os").path.exists(__import__("sys").prefix+"\\share_variables\\") and __import__("os").path.isdir(__import__("sys").prefix+"\\share_variables"):
    if __import__("os").path.isdir(__import__("sys").prefix+"\\share_variables\\"):
        __import__("os").remove(__import__("sys").prefix+"\\share_variables\\")
    __import__("os").mkdir(__import__("sys").prefix+"\\share_variables\\")

share_temp={}
UPLOAD="upload"
DELETE="delete"

def append(**kwargs):
    """Add the variable to temp,if variable in temp,set the variable."""
    for k,v in kwargs.items():
        share_temp[k]=v

def get_this_file(key:str=None)->dict:
    """get the keys variable,if keys is none,return the temp list,else return the key variable`s value."""
    assert isinstance(key,str)
    try:
        return share_temp[key]
    except KeyError:
        raise NameError(key+" is not in temp.")

def delete(key:str):
    """delete the temp keys."""
    assert isinstance(key,str)
    try:
        del share_temp[key]
    except KeyError:
        raise NameError(key+" is not in temp.")

def set(**kwargs):
    """Same as add."""
    for k,v in kwargs.items():
        share_temp[k]=v

def change(key:str,op,dv):
    """change the variable"""
    assert isinstance(key,str)
    try:
        share_temp[key]=op(share_temp[key],dv)
    except KeyError:
        raise NameError(key+" is not in temp.")

def in_temp(key:str,false_output=None,true_output=None):
    """Cho__import__("os")e the temp,if false_output is not None and key not in temp,print it and return False,else return True.
    if true_output is not None and key in temp,print it and return True,else return False."""
    assert isinstance(key,str)
    if false_output is not None and key not in share_temp:
        print(false_output)
    if true_output is not None and key in share_temp:
        print(true_output)
    return key in share_temp

def clear():
    "clear the temp."
    global share_temp
    share_temp={}

def share(do_type:str,share_name:str):
    assert isinstance(do_type,str),isinstance(share_name,str)
    "share the file variables."
    if do_type==UPLOAD:
        with open(__import__("sys").prefix+"\\share_variables\\"+share_name+".json","w",encoding="utf-8")as f:
            f.write("{")
            for k,v in share_temp.items():
                if type(v) is int or type(v) is bool:
                    f.write('"'+k+'":'+str(v).lower()+',')
                elif v is None:
                    f.write('"'+k+'":null,')
                else:
                    f.write('"'+k+'":"'+str(v)+'",')
            f.write("}")
        with open(__import__("sys").prefix+"\\share_variables\\"+share_name+".json","r",encoding="utf-8")as f:tmp=f.read().replace(",}","}")
        with open(__import__("sys").prefix+"\\share_variables\\"+share_name+".json","w",encoding="utf-8")as f:f.write(tmp)
    elif do_type==DELETE:
        __import__("os").remove(__import__("sys").prefix+"\\share_variables\\"+share_name+".json")
    else:
        raise KeyError("key"+str(type)+"is not a select.")

def get_share_file(share_name:str):
    assert isinstance(share_name,str)
    from json import load
    "get the share file variables."
    with open(__import__("sys").prefix+"\\share_variables\\"+share_name+".json","r",encoding="utf-8")as f:return load(f)
