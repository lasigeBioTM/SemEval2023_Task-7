import re

def unidades(line, ind):
    sum = -1
    index_check = ind
    words = []

    while index_check < len(line):
        if index_check == 0:
            sum = 1
        elif index_check == ind:
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
        index_check += sum

    return words

def unidades_finder(line, ind):
    print(line[ind])

with open('Training_data/Training_data/Clinical trial json/NCT02953860.json') as file:
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
                        #print("line: ",line)
                        print("words: ", words)
                    except:
                        #unidades_finder(line.split(), ind)
                        pass
#outras frases ficheiro NCT02953860
#falta ainda buscar 500mg [(500,'mg')]
"ANC >1000/uL and platelets >75,000/uL at screening visit"
"Total bilirubin < 1.5 times upper limit of normal (ULN) at the screening visit unless an alternate nonmalignant etiology exists (eg, Gilbert's disease)"


#exemplo resultados

"""
line:            Fulvestrant with Enzalutamide: 500mg of Fulvestrant will be given IM on days 1, 15, 28, then every 4 weeks as per standard of care (SOC) and 160mg of Enzalutamide will be given PO daily. Patients will receive a tumor biopsy at the start of treatment and 4 weeks after the start of treatment, with an optional 3rd biopsy at the end treatment.,

words:  [(1.0, 'days'), (1.0, 'then')]

line:            Fulvestrant with Enzalutamide: 500mg of Fulvestrant will be given IM on days 1, 15, 28, then every 4 weeks as per standard of care (SOC) and 160mg of Enzalutamide will be given PO daily. Patients will receive a tumor biopsy at the start of treatment and 4 weeks after the start of treatment, with an optional 3rd biopsy at the end treatment.,

words:  [(15.0, 'days'), (15.0, 'then')]

line:            Fulvestrant with Enzalutamide: 500mg of Fulvestrant will be given IM on days 1, 15, 28, then every 4 weeks as per standard of care (SOC) and 160mg of Enzalutamide will be given PO daily. Patients will receive a tumor biopsy at the start of treatment and 4 weeks after the start of treatment, with an optional 3rd biopsy at the end treatment.,

words:  [(28.0, 'days'), (28.0, 'then')]

line:            Fulvestrant with Enzalutamide: 500mg of Fulvestrant will be given IM on days 1, 15, 28, then every 4 weeks as per standard of care (SOC) and 160mg of Enzalutamide will be given PO daily. Patients will receive a tumor biopsy at the start of treatment and 4 weeks after the start of treatment, with an optional 3rd biopsy at the end treatment.,

words:  [(4.0, 'every'), (4.0, 'weeks')]

"""
