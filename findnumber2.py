import re

import os
import scispacy
import spacy
#from scispacy.abbreviation import AbbreviationDetector

units = ["%", "/ul", "/mm^3", "/mm^2", "/mm", "/ml", "/mml", "mg", "g", "kg"]

#### less tem que ser visto como < e bigger >


nlp = spacy.load("en_core_sci_sm")
#nlp.add_pipe("abbreviation_detector")
#text = " Times a day Fulvestrant with Enzalutamide: 500mg of Fulvestrant will be given IM on days 1, 15, 28, then every 4 weeks as per standard of care (SOC) and 160mg of Enzalutamide will be given PO daily. Patients will receive a tumor biopsy at the start of treatment and 4 weeks after the start of treatment, with an optional 3rd biopsy at the end treatment."

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


def rule_check(line, ind, number, index_check, entities, entao, dic):
    check = ["bigger than", "greater than", "less than", "smaller than"]
    check2 = ["<",">","<=",">="]
    new_phrase = " ".join(line)
    if any(ext in new_phrase for ext in check):
        if "less" == line[ind-2] and "than" == line[ind-1]: #se estiver à esquerda do número
            new_phrase =  new_phrase.replace("less than", "<")
            ind = ind - 1
            index_check -= 2

        elif "bigger" == line[ind-2] and "than" == line[ind-1]: 
            new_phrase =  new_phrase.replace("bigger than", ">")
            ind = ind - 1
            index_check -= 2

        elif "less" == line[ind+1] and "than" == line[ind+2]: # se estiver à direita
            new_phrase =  new_phrase.replace("less than", "<")
            if index_check > ind:
                index_check += 2
        elif "bigger" == line[ind+1] and "than" == line[ind+2]:
            new_phrase =  new_phrase.replace("bigger than", ">")
            if index_check > ind:
                index_check += 2
        entities = nlp(new_phrase).ents
    new_phrase = new_phrase.split()

    if ind + 1 < len(new_phrase) and index_check < len(new_phrase):
        if new_phrase[ind+1].lower() in check2:
            for ent in entities:
                if new_phrase[index_check].replace(",","").replace(".","").replace(":","") in str(ent):
                    if entao == None:
                        entao = [str(ent), number, new_phrase[ind+1]]
                        return entao
                    else:
                        entao.append(str(ent))
                        return entao
            #INR < 1.5 times ULN, or if on warfarin, can safely transition off for biopsy
            #INR 1.5 > times ULN, or if on warfarin, can safely transition off for biopsy
    
    if ind - 1 >= 0:
        if new_phrase[ind-1].lower() in check2:
            for ent in entities:
                if new_phrase[index_check].replace(",","").replace(".","").replace(":","") in str(ent):
                    if entao == None:
                        print("here")
                        if new_phrase[ind+1].lower() == "times":
                            dic["bigger/less"] = new_phrase[ind-1]
                            dic["<>side"] = "left"
                            dic["comparison"] = str(ent)
                            dic["number"] = number
                            dic["times"] = True
                            entao = [str(ent), new_phrase[ind-1], number, "times"]
                            return entao
                            
                        else:
                            entao = [str(ent), new_phrase[ind-1], number]
                            dic["bigger/less"] = new_phrase[ind-1]
                            dic["<>side"] = "left"
                            dic["comparison"] = str(ent)
                            dic["number"] = number
                            return dic
                    else:
                        dic["times what"] = str(ent)
                        entao.append(str(ent))
                        return dic


def unidades(line, ind, dic):
    text = " ".join(line)
    doc = nlp(text)
    entities = doc.ents
    sum = -1
    index_check = ind
    words = set()
    number = str(line[ind]).replace(",","")
    line.append(" ") #para verificar uma condição line[ind+1]
    entao = None
    while index_check < len(line):
        
        if index_check == ind:
            pass

        elif re.findall("\d+", line[index_check]):
            pass
        if entao == None:
            entao = rule_check(line, ind, number, index_check, entities, entao, dic)
        if entao:
            if sum == -1:
                sum = 1
            else:
                final = rule_check(line, ind, number, index_check, entities, entao, dic)
                if final != None: #ou seja, ser list
                    return final

        else:
            for ent in entities:
                if line[index_check].replace(",","").replace(".","").replace(":","") in str(ent):
                    if ind + 1 < len(line): #Alkaline phosphatase less than 2.5 times ULN*
                        if index_check == ind + 2 and "times" in line[ind+1].lower():
                            words.add((number, line[ind+1], str(ent))) 
                        else:
                            words.add((number, str(ent)))
                    else:
                        words.add((number, str(ent)))
                    if sum == -1:
                        sum = 1
                    else:
                        return words

        if index_check == 0:
            sum = 1
        index_check += sum

    return words
    
#o que está atrás de virgula não interessa ?
#CT03719677.json [('9', 'sessions'), ('9', 'coaching calls')]           Arm/Group Description: Treatment includes occupational therapy evaluation and consultation to address any deficits in physical function, safety, social participation and/or life roles. After the occupational therapy evaluation, the therapist delivers education on physical activity and dietary recommendations and habit development techniques, and uses behavioral skills training to develop habit plans, as well as prompts/cues, environmental modifications, and reminder text messages to reinforce engagement in the plan. The intervention is delivered through 3 face to face sessions, 9 tele coaching calls, and text messages.,#
#NCT00266110.json ('2.0', 'mg')           4.1.6 Serum Creatinine < 2.0 mg/dl. 4.1.7 Hepatic transaminases (alanine aminotransferase (ALT) and aspartate aminotransferase (AST)) 3.0 times the upper limit of normal if no liver metastases or 5 times the upper limit of normal if liver metastases are present.,
#NCT03719677.json ('50', 'mg')           A large waistline > 35 inches Blood pressure > 130/85; HbA1c of 5.7%-6.4%; Triglyceride levels > 150 mg/dL; HDL cholesterol levels < 50 mg/dL,
#130/85


def unidades_finder(line, ind, dic):
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
    print(other, "OTHERRRR")
    if len(other) > 1:
        for ent in entities:
            if other[1] in str(ent):
                return [(other[1], str(ent).replace(other[1], ""))]
                #return ((other[1], str(ent).replace(line[ind], "")))
             
        if other[2] == '': 
            return unidades(line,ind, dic)

        else:
            dic["unidade"] = str(other[2])

#done
#NCT00266110.json ('2.0', 'mg')           4.1.6 Serum Creatinine < 2.0 mg/dl. 4.1.7 Hepatic transaminases (alanine aminotransferase (ALT) and aspartate aminotransferase (AST)) 3.0 times the upper limit of normal if no liver metastases or 5 times the upper limit of normal if liver metastases are present.,
def time_finder(line, ind, dic):
    time_scale = ['daily', 'day', 'week', 'month', 'year', 'cycle', "%"]
    other = ["ul/", "mm", "ml", "mml", "mg", "kg", "cm" ]
    previous_index = 10
    save = False
    for time in time_scale:
        for index in range(len(line)):
            if time in line[index].lower():
                if abs(index-ind)<=5:
                    if abs(previous_index) > abs(index-ind):
                        save = time
                        previous_index = abs(index-ind)
    for unit in other:
        for index in range(len(line)):
            if unit in line[index].lower():
                if abs(index-ind)<=5:
                    if abs(previous_index) > abs(index-ind):
                        save = line[index]
                        previous_index = abs(index-ind)
    dic["unidade"] = save
    print("HERE")
            #elif other in line[index].lower():
            #    print("Here")
            #    if abs(index-ind)<=5:
            #        if abs(previous_index) > abs(index-ind):
            #            save = line[index]
            #            previous_index = abs(index-ind)

    return dic


#to_write = open("results_check.tsv", "w")
#to_write.write("filename\tlocation\twords\tline\n")

exclude = ["Results", "Eligibility", "Inclusion Criteria", "Clinical Trial ID", "Intervention", 
            "INTERVENTION", "Outcome Measurement", "Adverse Events", "Exclusion Criteria"]
location = ""

for (root, dir_path, files) in os.walk('Training_data/Training_data/Clinical trial json/'):
    for filename in ["NCT00003782.json", "NCT02953860.json"]:# #files:
        with open('Training_data/Training_data/Clinical trial json/' + filename) as file: #NCT00003782NCT02953860
            for line in file.readlines():
                
                #line = "INR 1.5  bigger than times ULN, or if on warfarin, can safely transition off for biopsy"
                if any(ext in line for ext in exclude):
                    location = [ext for ext in exclude if ext in line]
                
                #line = "INR < 1.5 times ULN, or if on warfarin, can safely transition off for biopsy"
                #line = line.replace(",",".")
                    
                else:

                    dic = {"filename": filename, "line": line, "location": location, "n_pos": None, 
                    "number": None, "unidade": None, "of": None, "comparison": None, 
                    "bigger/less": None, "<>side": None, "times": None, "times what": None}

                    if re.findall("\d+", line):
                        numbers = re.findall("\d+", line) #só para ver
                        line = line.replace('"','') #tirar aspas das frases
                        for ind in range(len(line.split())):
                            if re.findall("\d+", line.split()[ind]):
                                #print(line, re.findall("\d+", line.split()[ind]))
                                try:
                                    float(line.split()[ind].replace(",","."))#.replace(":",""))#caso tenha virgula 1,0 não será aceite
                                    dic = time_finder(line.split(), ind, dic)
                                    dic["n_pos"] = ind
                                    dic["number"] = line.split()[ind]
                                    dic = unidades(line.split(), ind, dic)
                                    
                                    for key in dic:
                                        print(key+": ", dic[key])

                                    #if len(words) == 1: #porque pode ter dois VER ISTO AINDA
                                    #for word in words:
                                    #    drugs = drug_finder(line.split(), ind, word)
                                    #    print("line: ",line)
                                    #    print("words: ", words)
                                    #    print("drugs: ", drugs, '\n')
                                except:
                                    #words = unidades_finder(line.split(), ind, dic)
                                    #print(filename, words, line)
                                    #if words != None:
                                    #    for word in words:
                                    #        print("line: ",line)
                                    #        print("words: ", words)
                                    #        drugs = drug_finder(line.split(), ind, word)
                                    #        print("drugs: ", drugs, '\n')
                                    pass
                                #to_write.write(filename+"\t" + location[0] + "\t" + str(words)+"\t" + line+"\n")


"""

line:          "  INR < 1.5 times ULN, or if on warfarin, can safely transition off for biopsy",

location:  ['Inclusion Criteria']
n_pos:  2
number:  1.5
unidade:  False
of:  None
comparison:  INR
bigger/less:  <
<>side:  left
times:  True
times what:  ULN

filename:  NCT02953860.json
line:          "  Creatinine < 1.5 times ULN",

location:  ['Inclusion Criteria']
n_pos:  2
number:  1.5
unidade:  False
of:  None
comparison:  Creatinine
bigger/less:  <
<>side:  left
times:  True
times what:  ULN


"""
