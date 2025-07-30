def xml_to_json(xmlFile:str,jsonFile:str | None = None):
    from xmltodict import parse
    from json import dumps
    from math import floor

    tab  =[]
    repS = []

    with open(xmlFile,"r",encoding="utf-8") as f:
        json = dumps(parse(f.read()),indent=4)

    for i in range(len(json.splitlines())):
        line_string = json.splitlines()[i]
        first_char = line_string[0]
        count = 1      
        for c in line_string[1:]:
            if c == first_char:
                count += 1
            else:
                break
        tab.append(floor(count/4))
        count = len(json.splitlines()[i]) - len(json.splitlines()[i].lstrip())
        new_s = json.splitlines()[i].replace(' ', '', count)
        try:
            if new_s[0]+new_s[1] == '"@':
                new_s='"'+new_s[2:]
        except:
            pass
        repS.append(new_s)

    for i in range(len(repS)):
        repS[i]="    "*tab[i]+repS[i]+"\n"

    if jsonFile is not None:
        with open(jsonFile,"w",encoding="u8") as f:
            f.writelines(repS)

    return "".join(repS)

def csv_to_tsv(csvFile:str,tsvFile:str | None = None):
    with open(csvFile,"r",encoding="utf-8") as f:
        csv = f.readlines()

    o = []
    for i in csv:
        o.append(i.replace(",","\t"))
    
    if tsvFile is not None:
        with open(tsvFile,"w",encoding = "utf-8") as f:
            f.writelines(o)
    return o

def tsv_to_csv(tsvFile:str,csvFile:str | None = None):
    with open(tsvFile,"r",encoding="utf-8") as f:
        csv = f.readlines()
    o = []
    
    for i in csv:
        o.append(i.replace("\t",","))
    
    if csvFile is not None:
        with open(csvFile,"w",encoding = "utf-8") as f:
            f.writelines(o)
    return o

def csv_to_json(csvFile:str,jsonFile:str | None = None):
    with open(csvFile,"r",encoding="utf-8") as f:
        csv=f.readlines()

    o:list[list[int | str]]=[]
    k=0
    for i in csv:
        o.append([])
        for j in i:
            for l in j.split(","):
                try:
                    if l!="":
                        o[k].append(int(l))
                except Exception as e:
                    o[k].append(l)
        k+=1
        
    r=0
    l=0
    for i in o:
        for k in i:
            if k == "\n":
                del o[r][l]
            l += 1
        l = 0
        r += 1
    
    if jsonFile is not None:
        with open(jsonFile,"w",encoding = "utf-8") as f:
            f.writelines(str(o).replace("'",'"'))
    
    return o

def tsv_to_json(tsvFile:str,jsonFile:str | None = None):
    with open(tsvFile,"r",encoding="utf-8") as f:
        csv = f.readlines()

    o:list[list[int | str]]=[]
    k = 0
    for i in csv:
        o.append([])
        for j in i:
            for l in j.split("\t"):
                try:
                    if l!="":
                        o[k].append(int(l))
                except Exception as e:
                    o[k].append(l)
        k += 1
        
    r = 0
    l = 0
    for i in o:
        for k in i:
            if k=="\n":
                del o[r][l]
            l += 1
        l = 0
        r += 1
    
    if jsonFile is not None:
        with open(jsonFile,"w",encoding="utf-8") as f:
            f.writelines(str(o).replace("'",'"'))
    
    return o

def json_to_xml(jsonFile,xmlFile:str | None=None):
    '''this is beta version.'''
    import json
    from xml.etree.ElementTree import Element,tostring

    with open(jsonFile,"r",encoding="utf-8") as f:
        json_obj=json.load(f)

    if isinstance(json_obj, dict):
        element = Element(json_obj.get('tag', 'root'))
        for key, value in json_obj.items():
            if key == 'tag':
                continue  # Skip the 'tag' key
            sub_element = Element(key)
            sub_element.text = str(value)
            element.append(sub_element)
    elif isinstance(json_obj, list):
        element = Element('root')
        for item in json_obj:
            sub_element = Element('item')
            if isinstance(item, dict):
                for k, v in item.items():
                    sub_sub_element = Element(k)
                    sub_sub_element.text = str(v)
                    sub_element.append(sub_sub_element)
            else:
                sub_element.text = str(item)
            element.append(sub_element)

    o = (tostring(element, encoding='utf-8', method='xml', xml_declaration=True).decode('utf-8')).splitlines()[1]
    if xmlFile is not None:
        with open(xmlFile,"w",encoding="utf-8") as f:
            f.write(o)
    return o
