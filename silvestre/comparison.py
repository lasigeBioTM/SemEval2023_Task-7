import json, os
import re
import spacy


from readfile import File

#########
#Comparison
#########

def rl_check(sentence, number, ind, signal, right_left, entities, dic):
    """
    function that checks if number is in left or right side of <>
    and what is it comparing.
    sentence: string input
    number: number to check if is in comparison
    singal: <> <= >=
    entities: set of entities
    dic: dictionary to change
    return dic
    """
    sentence = " ".join(sentence)
    #print(number)
    #print(entities)
    numb_ind = sentence.find(signal)
    neg_ind = {}
    pos_ind = {}
    #print(entities)
    for ent in entities:
        where = [pos.start() - numb_ind for pos in re.finditer(str(ent),sentence)]
        for pos in where:
            if pos < 0: 
                neg_ind[pos] = str(ent)

            elif pos >0: 
                pos_ind[pos] = str(ent)

    if neg_ind != {} and pos_ind != {}:
        
        close_neg = sorted(neg_ind, reverse = True)[0]
        close_pos = sorted(pos_ind)[0]
        if right_left == "right":
            dic["bigger/less"] = signal
            dic["<>side"] = right_left
            dic["times what"] = neg_ind[close_neg]
            dic["number"] = number
            dic["comparison"] = pos_ind[close_pos]
            if "times" in sentence.lower():
                where = [pos.start() - numb_ind for pos in re.finditer("times",sentence.lower())]
                for pos in where:
                    if pos < ind and pos > close_neg or pos>ind and pos < close_neg:
                        dic["times"] = True
        else:
            
            dic["bigger/less"] = signal
            dic["<>side"] = right_left
            dic["times what"] = pos_ind[close_pos]
            dic["number"] = number
            dic["comparison"] = neg_ind[close_neg]
            if "times" in sentence.lower():
                where = [pos.start() - numb_ind for pos in re.finditer("times",sentence.lower())]
                for pos in where:
                    if pos < ind and pos > close_pos or pos>ind and pos < close_pos:
                        dic["times"] = True

        return dic

def comparison(line, ind, dic):
    """
    function that will check if the number is in a comparison.
    line: list of words
    ind: position of number
    dic: dictionary to change
    return dic
    """
    check = ["bigger than", "greater than", "less than", "smaller than"]
    check2 = ["<",">","<=",">="]
    number = line[ind]
    new_phrase = " ".join(line)

    if not any(ext in new_phrase for ext in check) and not any(ext in new_phrase for ext in check2):
        return dic

    if any(ext in new_phrase for ext in check):
        if "bigger than" in new_phrase:
            new_phrase =  new_phrase.replace("bigger than", "<")
        elif "less than" in new_phrase:
            new_phrase =  new_phrase.replace("less than", "<")
    entities = nlp(new_phrase).ents
    new_phrase = new_phrase.split()
    if ind > len(new_phrase):
        return print("WHYYYYYYY", ind, new_phrase)
    if new_phrase[ind] != number:
        ind -= 1

    for i in range(-4,4):
        if ind + i < len(new_phrase) and ind + i >= 0:
            if i > 0:
                #ind muda então tenho que mudar

                if new_phrase[ind+i].lower() in check2: #INR 1.5 > ULN
                    
                    signal = new_phrase[ind+i]
                    rl_check(new_phrase, number, ind, signal,"right", entities, dic)
            elif i < 0:

                if new_phrase[ind+i].lower() in check2:
                    signal = new_phrase[ind+i]
                    rl_check(new_phrase, number, ind, signal,"left", entities, dic)
    return dic

def print_comp(dic):
    print(dic["line"])
    if dic["<>side"] == "left":
        if dic["times"] == None:
            to_print = [dic["comparison"], dic["bigger/less"], dic["number"], dic["times what"]]
        else:
            to_print = [dic["comparison"], dic["bigger/less"], dic["number"], dic["times"], dic["times what"]]
        print(to_print)

    elif dic["<>side"] == "right":
        if dic["times"] == None:
            to_print = [dic["number"], dic["times what"], dic["bigger/less"], dic["comparison"]]
            
        else:
            to_print = [dic["number"], dic["times"], dic["times what"], dic["bigger/less"], dic["comparison"]]
        print(to_print)

#nlp = spacy.load("en_core_sci_sm")
#nlp = spacy.load("en_core_sci_lg")
#nlp.add_pipe("abbreviation_detector")
#text = " Times a day Fulvestrant with Enzalutamide: 500mg of Fulvestrant will be given IM on days 1, 15, 28, then every 4 weeks as per standard of care (SOC) and 160mg of Enzalutamide will be given PO daily. Patients will receive a tumor biopsy at the start of treatment and 4 weeks after the start of treatment, with an optional 3rd biopsy at the end treatment."
#nlp = spacy.load("en_core_sci_scibert")
#nlp = spacy.load("en_core_web_sm")
nlp = spacy.load("en_ner_bionlp13cg_md") #NER	

#nlp.add_pipe("merge_entities")
#nlp.add_pipe("merge_noun_chunks")

#abrir ficheiro e guardar locais
files = set()

with open('Training_data/Training_data/train.json') as file:
    data = json.load(file)
    for x in data:
        f = File(data[x]["Primary_id"], data[x]["Statement"], data[x]["Label"])
        files.add(f)
        if os.path.exists("Training_data/Training_data/Clinical trial json/"+f.filename+".json"): #alguns não existem
            with open("Training_data/Training_data/Clinical trial json/"+f.filename+".json") as file2:
                data2 = json.load(file2)
                [f.addSentence(y,data2[y]) for y in data2 if y != "Clinical Trial ID"]


#abrir frases
for file in files:
    sentences = [sent for loc in file.getSentences() for sent in file.getSentences(loc)]
    """
    if file.getFilename() in ["NCT00003782", "NCT02953860"]:
        sentences = [sent for loc in file.getSentences() for sent in file.getSentences(loc)]
    else:
        sentences = []
    """
    for loc in sentences:
        for sent in loc:
            if re.findall("\d+", sent):
                for ind in range(len(sent.split())):
                    try:
                        if re.findall("\d+", sent.split()[ind]):
                            dic = {"filename": file.filename, "line": sent, "location": "LATER ALLIGATOR", "index": None, 
                                    "number": None, "unidade": None, "of": None, "comparison": None, 
                                    "bigger/less": None, "<>side": None, "times": None, "times what": None}
                            dic = comparison(sent.split(), ind, dic)
                            if dic["comparison"]:
                                dic["index"] = ind
                                dic["number"] = sent.split()[ind]
                                print_comp(dic)
                    except: pass

