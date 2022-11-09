import re

import scispacy
import spacy
#from scispacy.abbreviation import AbbreviationDetector

units = ["%", "/ul", "/mm^3", "/mm^2", "/mm", "/ml", "/mml", "mg", "g", "kg"]

nlp = spacy.load("en_core_sci_sm")
#nlp.add_pipe("abbreviation_detector")
text = " Times a day Fulvestrant with Enzalutamide: 500mg of Fulvestrant will be given IM on days 1, 15, 28, then every 4 weeks as per standard of care (SOC) and 160mg of Enzalutamide will be given PO daily. Patients will receive a tumor biopsy at the start of treatment and 4 weeks after the start of treatment, with an optional 3rd biopsy at the end treatment."

def ent_position(line, ind):
    doc = nlp(" ".join(line))
    line[ind] = "WORD_"
    text = " ".join(line)
    
    word_pos = text.find("WORD_")
    #pos = {'WORD_': text.find("WORD_")}
    pos = dict()
    entities = []
    for ent in doc.ents: #ent não são str pelo que não dá para dar sort pelo tamanho
        if str(ent) not in entities:
            entities.append(str(ent))
    entities = sorted(entities , key = len, reverse= True)

    for ent in entities:
        pos[ent] = [m.start() for m in re.finditer(re.escape(ent), text)]
        text = text.replace(ent, 'A' * len(ent))

    lista = [word_pos]
    for key in pos:
        for value in pos[key]:
            lista.append(value)
    lista = sorted(lista)
    index = lista.index(word_pos)
    #print(lista)
    #print(pos)

    close_ent = []
    #print(index, pos)
    if index == 0:
        if index + 1 < len(lista): #este pôde-se tirar depois de editar o drug_finder
            close_ent.append(lista[index+1])
        if index + 2 < len(lista): #ou seja, se não for o último
            close_ent.append(lista[index+2])
    elif  index > 0:
        if index - 1 >= 0:
            close_ent.append(lista[index-1])
        if index + 1 < len(lista):
            close_ent.append(lista[index+1])
        if index - 2 >= 0:
            close_ent.append(lista[index-2])
        if index + 2 < len(lista):
            close_ent.append(lista[index+2])
        
    keys = []
    for pos_ent in close_ent:
        for key in pos:
            if pos_ent in pos[key]:
                keys.append(key)
    return keys




#ent_position(text.split(), 2)

def drug_finder(line, ind, identified):
    text = " ".join(line)
    doc = nlp(text)
    entities = doc.ents
    index_check = ind
    sum = -1
    if len(entities) == 0:
        return(None, identified[0], identified[1])
    elif ind+1< len(line): 
        if line[ind + 1] == "of": #caso seja of something
            text = re.sub(r'^.*?%s'%line[ind],line[ind], text)
            removed = " ".join(line).replace(text, "") #para remover entities antes disto porque se aparecer duplicado pode identificar mal o of
            remaining = []
            for ent in entities:
                if str(ent) in removed:
                    removed = removed.replace(str(ent)," ") #tem que se editar o texto
                else:
                    remaining.append(ent)
            for ent in remaining:
                if str(ent) in text:
                    return (ent, identified[0], identified[1])
    
    #editar
        else:
            ents = ent_position(line, ind)
            #return(None, identified[0][0], identified[0][1])
    else:
        ents = ent_position(line, ind)
    
    if ents != []:
        possibilities = [(ent, identified[0], identified[1]) for ent in ents]
        return possibilities
    else:
        return (None, identified[0], identified[1])
        
    
        
            
    """
    while index_check < len(line):
        if index_check == ind:
            pass
        elif re.findall("\d+", line[index_check]):
            pass
        elif line[index_check] == "<" or line[index_check] == ">":
            pass
        else:  
            words.append((float(line[ind].replace(",",".")),line[index_check]))
            if sum == -1:
                sum = 1
            else:
                return words

        if index_check == 0:
            sum = 1

        index_check += sum

    return words"""

def unidades(line, ind, other = False):
    text = " ".join(line)
    doc = nlp(text)
    entities = doc.ents
    sum = -1
    index_check = ind
    words = []

    while index_check < len(line):
        if index_check == ind:
            pass
        elif re.findall("\d+", line[index_check]):
            pass
        elif line[index_check] == "<" or line[index_check] == ">":
            pass
        else:
            if other:
                
                #if line[index_check] in str(entities):
                words.append((other, line[index_check]))
                pass
            else:
                #if line[index_check] in entities:
                words.append((float(line[ind].replace(",",".")),line[index_check]))
            if sum == -1:
                sum = 1
            else:
                return words

        if index_check == 0:
            sum = 1

        index_check += sum

    return words

def unidades_finder(line, ind):
    """caso o número tenha algo colado a ele e não tenha sido identificado"""
    #print(line)
    text = " ".join(line)
    doc = nlp(text)
    entities = doc.ents
    #print(text, entities)
    number = re.sub(r"[\[].*?[\]]", '', line[ind]) #tirar valores entre [] [1]1/32 fica 1/32
    #print("NUMBER: ", number, "line: ", line[ind])
    number = number.replace("(","").replace(")","").replace(":"," ")
    other = re.split(r'(\d+.\d+)', number.replace(",",""))

    if len(other) > 1:
        for ent in entities:
            if other[1] in str(ent):
                return [(other[1], str(ent).replace(other[1], ""))]
                #return ((other[1], str(ent).replace(line[ind], "")))
             
        if other[2] == '': 
            return unidades(line,ind, other[1])

        else:
            return [(other[1], other[2])]


with open('Training_data/Training_data/Clinical trial json/NCT02953860.json') as file: #NCT00003782
    for line in file.readlines():
        #line = line.replace(",",".")
        if re.findall("\d+", line):
            numbers = re.findall("\d+", line) #só para ver
            line = line.replace('"','') #tirar aspas das frases
            for ind in range(len(line.split())):
                if re.findall("\d+", line.split()[ind]):
                    #print(line, re.findall("\d+", line.split()[ind]))
                    try:
                        float(line.split()[ind].replace(",","."))#.replace(":",""))#caso tenha virgula 1,0 não será aceite
                        words = unidades(line.split(), ind)
                        #print("WORDS: ", words)
                        #if len(words) == 1: #porque pode ter dois VER ISTO AINDA
                        for word in words:
                            drugs = drug_finder(line.split(), ind, word)
                            print("line: ",line)
                            print("words: ", words)
                            print("drugs: ", drugs, '\n')
                    except:
                        words = unidades_finder(line.split(), ind)
                        if words != None:
                            for word in words:
                                print("line: ",line)
                                print("words: ", words)
                                drugs = drug_finder(line.split(), ind, word)
                                print("drugs: ", drugs, '\n')
                        pass


#tem que se verificar se o que foi identificado é doença ou não em vez de unidade
"ANC >1000/uL and platelets >75,000/uL at screening visit"
#ANC >1000/uL and platelets >75,000/uL at screening visit,
#['platelets', 'screening visit', 'ANC'] Apanha todos os tokens neste caso
"Total bilirubin < 1.5 times upper limit of normal (ULN) at the screening visit unless an alternate nonmalignant etiology exists (eg, Gilbert's disease)"

"words:  [('02953860', 'ID:')]"
"drugs:  [('ID', '02953860', 'ID:'), ('Clinical Trial', '02953860', 'ID:')] "

"""
line:            500mg of Fulvestrant will be given IM on days 1, 15, 28, then every 4 weeks as per standard of care (SOC) and 160mg of Enzalutamide will be given, in conjunction with Fulvestrant, PO daily.,

words:  [(1.0, 'days'), (1.0, 'then')]
drugs:  [('days', 1.0, 'days'), ('weeks', 1.0, 'days'), ('IM', 1.0, 'days'), ('standard of care', 1.0, 'days')]
"""
