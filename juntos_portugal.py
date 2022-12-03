import os
import scispacy
import spacy

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("merge_entities")
nlp.add_pipe("merge_noun_chunks")



exclude = ["Results", "Eligibility", "Inclusion Criteria", "Clinical Trial ID", "Intervention", 
            "INTERVENTION", "Outcome Measurement", "Adverse Events", "Exclusion Criteria"]
location = ""


for (root, dir_path, files) in os.walk('Training_data/Training_data/Clinical trial json/'):
    for filename in ["NCT00003782.json", "NCT02953860.json"]:# #files:
        with open('Training_data/Training_data/Clinical trial json/' + filename) as file: #NCT00003782NCT02953860
            for line in nlp.pipe(file.readlines()):
                if any(ext in str(line) for ext in exclude):
                    location = [ext for ext in exclude if ext in str(line)]
                
                #line = "INR < 1.5 times ULN, or if on warfarin, can safely transition off for biopsy"
                #line = line.replace(",",".")
                    
                else:
                    print(line)
                    for l in line: 
                        #print( "---", l, l.pos_
                        if "Fulvestrant" in str(l):
                            print("FUV", l.dep_)
                        if l.pos_ == "NUM":
                            print("______")
                            print(l.ent_type_)
                            print(l)
                            print("HERE", l, l.head.text)
                            print("HERE", l, l.head.head)
                            print("here", l, [(child, child.dep_) for child in l.children])
                            print(l.head.lemma_)
                            #print(l)
                            if l.dep_ == "pobj" and l.head.dep_ == "prep":
                                print("XXX", l.head.head, "-->", l)
                    """
                    if l.ent_type_:
                        #print(l.ent_type_, l)
                        if l.dep_ in ("attr", "dobj"):
                            subj = [w for w in l.head.lefts if w.dep_ == "nsubj"]
                            if subj:
                                print(line, subj[0], "-->", l)
                        elif l.dep_ == "pobj" and l.head.dep_ == "prep":
                            print(l, l.head.head, "--->", l)"""
                        

"""
"  Arm/Group Description: 500mg of Fulvestrant will be given IM on days 1, 15, 28, then every 4 weeks as per standard of care (SOC) and 160mg of Enzalutamide will be given, in conjunction with Fulvestrant, PO daily.",

15
28
160
1 não está presente porque? porque está com days 1

"""
