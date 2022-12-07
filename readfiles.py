import os
import json

files = set()

class File:
    def __init__(self, filename, statement, label):
        self.filename = filename
        self.statement = statement
        self.label  = label
        self.sentences = {}
        files.add(self)
    
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


#Criar items
with open('Training_data/Training_data/train.json') as file:
    data = json.load(file)
    for x in data:
        f = File(data[x]["Primary_id"], data[x]["Statement"], data[x]["Label"])
        if os.path.exists("Training_data/Training_data/Clinical trial json/"+f.filename+".json"):
            with open("Training_data/Training_data/Clinical trial json/"+f.filename+".json") as file2:
                data2 = json.load(file2)
                [f.addSentence(y,data2[y]) for y in data2 if y != "Clinical Trial ID"]



for file in files:
    
    #print(file.getStatement())
    if "less" in file.getStatement().lower(): 
        print(file.getFilename())
        print(file.getStatement().lower())
    #for x in file.getSentences():
    #    print([y for y in file.getSentences(x)])
