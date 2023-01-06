import os
import json


class File:
    files = set()
    def __init__(self, filename, statement, label):
        self.filename = filename
        self.statement = statement
        self.label  = label
        self.sentences = {}

    def addSentence(self, location, add):
        if location not in self.sentences:
            self.sentences[location] = [add]
        else:
            self.sentences[location].append(add)
    
    def getSentences(self, location = None):
        if location == None:
            return self.sentences
        else:
            return self.sentences[location]
    
    def getLabel(self):
        return self.label
    
    def getStatement(self):
        return self.statement
    
    def getFilename(self):
        return self.filename






files = set()
#Criar items
with open('Training_data/Training_data/train.json') as file:
    data = json.load(file)
    for x in data:
        f = File(data[x]["Primary_id"], data[x]["Statement"], data[x]["Label"])
        files.add(f)
        if os.path.exists("Training_data/Training_data/Clinical trial json/"+f.filename+".json"):
            with open("Training_data/Training_data/Clinical trial json/"+f.filename+".json") as file2:
                data2 = json.load(file2)
                [f.addSentence(y,data2[y]) for y in data2 if y != "Clinical Trial ID"]


for file in files:
    if file.getFilename() == "NCT00003830":
        print(file.getFilename())
        print(file.getLabel() + "\n")
        print(file.getStatement() + "\n")
        print(file.getSentences("Intervention"))
    #print(file.getStatement())
    #if "less" in file.getStatement().lower(): 
    #    print(file.getFilename())
        #print(file.getStatement())
    #for x in file.getSentences():
    #    print([y for y in file.getSentences(x)])

