import json, os
import re
import spacy
import operator
import string
#import inflect

from readfile import File

#nlp_sci = spacy.load("en_core_sci_scibert")

nlp = spacy.load("en_core_sci_sm")
nlp_sci = spacy.load("en_ner_bionlp13cg_md") #NER	

nlp_sci.add_pipe("merge_entities")
nlp_sci.add_pipe("merge_noun_chunks")


ops = {
    '+' : operator.add,
    '-' : operator.sub,
    '*' : operator.mul,
    '/' : operator.truediv,  # use operator.div for Python 2
    '%' : operator.mod,
    '^' : operator.xor
    }
letters = string.ascii_letters


def check_more(sent):
    """
    function that receives sent and will check for all tokens,
    if it has children, lefts and rights.
    ------
    sent: string of a sentence
    ------
    returns
    check: dictionary of tokens
    """
    check = {}
    sent_sci = nlp_sci(sent)
    for ind, token in enumerate(sent_sci):
        check[(token.text, ind)] = {"children": [children for children in token.children]}
        check[(token.text, ind)]["lefts"] = [lefts for lefts in token.head.lefts]
        check[(token.text, ind)]["rights"] = [rights for rights in token.head.rights]
        return check



def join_dicts(check, dic, time):
    """"
    function that receives check, dic and time and will merge dictionaries
    if there is time associated with the tokens present in dic.
    -------
    check: dictionary of tokens
    dic: dictionary of numeric tokens
    time: dictionary of time measures
    -------
    returns
    dic: dictionary of numeric tokens
    """
    time_scale = ['daily', 'day', 'week', 'month', 'year', 'cycle']
    def join_dicts2(ent):
        if "daily" in str(rights).lower():
            dic[ent]["days"] = ["daily"]
        for t in time:
            if str(t[0]) in str(rights):
                dic[ent][str(t[0])] = time[t]

    for ent in dic:
        for ent2 in check:
            lefts = check[ent2]["lefts"]
            children = check[ent2]["children"]
            rights = check[ent2]["rights"]
            if str(ent[0])[-2:] == ".0" and str(ent[0]).replace(".0", "") in str(ent2[0]):
                if "of" in dic[ent]:
                    if str(dic[ent]["of"]) in str(children):
                        if any([x in str(rights) for x in time_scale]):
                            join_dicts2(ent)
    return dic



def split_numbers(number, sent_split, ind):
    """
    if number is 3rd or 1000/uL it will return 3rd and 1000, uL
    """
    number = number.replace("(","").replace(")","").replace(":"," ")
    if number[-2:] in ["rd","st","nd","th"]: #1st, 2nd
        return (number, sent_split[ind+1])
    #other = re.split(r'(\d+)', number.replace(",",""))
    other = number.split("/")
    if len(other) == 2:
        return (other[0], "/"+other[1])

""" #not used
def get_time(sent):
    sent = nlp_sci(sent)
    time_scale = ['daily', 'day', 'week', 'month', 'year', 'cycle']
    dic = {}
    for ind, word in enumerate(sent):
        for time in time_scale:
            if time in word.text:
                if word.text not in dic:
                    dic[word.text] = {"children": [children for children in word.children], "lefts": [lefts for lefts in word.head.lefts], 
                        "rights": [right for right in word.head.rights]}
                else:
                    dic[word.text]["children"].append([children for children in word.children])
                    dic[word.text]["lefts"].append([lefts for lefts in word.head.lefts])
                    dic[word.text]["rights"].append([right for right in word.head.rights])
    return dic
"""

def get_left_ent(number, sent_split, ind):
    """
    get entities in the left of number
    """
    for i in range(ind-1, 0, -1):
        for ent in sent_split.ents:
            #print(ent)
            if sent_split[i].text in str(ent):
                #print(ent)
                return str(ent).replace(number, "")
                #print(str(ent).replace(number, ""), "AI AI")

""" #not used
def get_right_ent(number, sent_split, ind):
    for i in range(ind+1, len(sent_split)):
        for ent in sent_split.ents:
            if sent_split[i].text in str(ent):
                print(str(ent).replace(number, ""), "AI AI")
"""

def check_division(number):
    """check if the number is a division -> 1/7"""

    number = re.sub(r"[\[].*?[\]]", '', number) #tirar valores entre [] [1]1/32 fica 1/32
    #print("NUMBER: ", number, "line: ", line[ind])
    number = number.replace("(","").replace(")","").replace(":"," ")
    #other = re.split(r'(\d+.\d+)', number.replace(",",""))
    #print(number)
    return number



def time_finder(sent_split, ind):
    """will check if there is any time_scale in sentence and 
    if so, wil check the number of the day, etc"""
    time_scale = ['daily', 'day', 'week', 'month', 'year', 'cycle']
    previous_index = 10
    save = False
    for index in range(len(sent_split)):
        if any([time in sent_split[index].text for time in time_scale]):
            if abs(index-ind) <= 5:
                if abs(previous_index) > abs(index-ind):
                    previous_index = abs(index-ind)
                    save = sent_split[index].text, index, sent_split[ind].text
    return save


def sent_checker(sent, sent_split):
    """
    function that receives sent and sent_split. It will check
    if the sentence contains numbers. If it contains numbers, than
    it will return a dic of the numbers present in the sentence
    and its quantity measure, what substance it is and the days it 
    is taken if possible.
    ------
    sent: string sentence
    sent_split: class os nlp tokens
    ------
    returns:
    dic: dictionary
    """
    entities = sent_split.ents
    #time = get_time(sent)
    dic = {}
    times = {}
    time_scale = ['daily', 'day', 'week', 'month', 'year', 'cycle']
    check = check_more(sent)
    for ind, token in enumerate(sent_split):
        if re.findall("\d+", token.text):

            if any([x in token.text for x in ops]) and not any([x in token.text for x in letters]): #PODE SER 1,500/mm3
                number = check_division(token.text)
                #print("AQUI",sent_split.ents)
                left_ent = get_left_ent(token.text, sent_split, ind)
                dic[(number, ind)] = {"of": left_ent}

            else:
                try:
                    number = float(str(token.text).replace(",",".")) #check if possible
                    time = time_finder(sent_split, ind) #ver se é dia ou semana etc DONE
                    
                    if time:
                        if (time[0], time[1]) not in times:
                            times[(time[0], time[1])] = [number]
                        else:
                            times[(time[0], time[1])].append(number)

                    elif ind < len(sent_split) - 1: 
                        if sent_split[ind+1].pos_ == "NOUN":
                            time_check = [time in sent_split[ind+1].text for time in time_scale] 
                            if True not in time_check:
                                dic[(number, ind)] = {"measure": sent_split[ind+1]}
                                if str(sent_split[ind+2]) == "of":
                                    dic[(number, ind)]["of"] = sent_split[ind+3]
                                #print("number: ", number, "index: ", ind, "unidade: ", sent_split[ind+1])
                    if "participants" in str(sent_split).lower():
                        if "analyzed" in str(sent_split).lower():
                            dic[(number, ind)]={"of":"Participants Analyzed"}
                            #print(number, "Participants Analyzed", sent_split)
                        else:
                            dic[(number, ind)]={"of":"Participants"}
                            #print(number, "Participants", sent_split)



                except:
                    split = split_numbers(token.text, sent_split, ind)
                    if split:
                        dic[(split[0], ind)] = {"measure": split[1]}

    #print(sent)
    return join_dicts(check, dic, times)


files = set()


#READFILE.PY
with open('Training_data/Training_data/train.json') as file:
    data = json.load(file)
    for x in data:
        f = File(data[x]["Primary_id"], data[x]["Statement"], data[x]["Label"])
        files.add(f)
        if os.path.exists("Training_data/Training_data/Clinical trial json/"+f.filename+".json"): #alguns não existem
            with open("Training_data/Training_data/Clinical trial json/"+f.filename+".json") as file2:
                data2 = json.load(file2)
                [f.addSentence(y,data2[y]) for y in data2 if y != "Clinical Trial ID"]

#VAI BUSCAR AS FRASES
for file in files:
    sentences = [sent for loc in file.getSentences() for sent in file.getSentences(loc)]
    """
    if file.getFilename() in ["NCT00003782", "NCT02953860"]: #apenas estes dois ficheiros 
        sentences = [sent for loc in file.getSentences() for sent in file.getSentences(loc)]
    else:
        sentences = []
    """
    for loc in sentences: #SENTENCES É UMA LISTA DE LISTA DE SENTENCES
        for sent in loc: #VAI BUSCAR A SENTENCE

            ##########################É ISTO QUE QUERES PARA BAIXO###################################

            if re.findall("\d+", sent): #caso haja números na frase
                sent_split = nlp(sent) 
                #sent = nlp(sent)
                print("final->", sent, sent_checker(sent, sent_split))  #É ASSIM QUE CHAMAS O sent_checker

