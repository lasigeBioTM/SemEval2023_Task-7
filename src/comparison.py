#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, os, re, spacy

nlp = spacy.load("en_ner_bionlp13cg_md")  # NER

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

    numb_ind = sentence.find(signal)
    neg_ind = {}
    pos_ind = {}

    for ent in entities:
        where = [pos.start() - numb_ind for pos in re.finditer(str(ent), sentence)]
        for pos in where:
            if pos < 0:
                neg_ind[pos] = str(ent)

            elif pos > 0:
                pos_ind[pos] = str(ent)

    if neg_ind != {} and pos_ind != {}:

        close_neg = sorted(neg_ind, reverse=True)[0]
        close_pos = sorted(pos_ind)[0]
        if right_left == "right":
            dic["bigger/less"] = signal
            dic["<>side"] = right_left
            dic["times what"] = neg_ind[close_neg]
            dic["number"] = number
            dic["comparison"] = pos_ind[close_pos]
            if "times" in sentence.lower():
                where = [pos.start() - numb_ind for pos in re.finditer("times", sentence.lower())]
                for pos in where:
                    if pos < ind and pos > close_neg or pos > ind and pos < close_neg:
                        dic["times"] = True
        else:

            dic["bigger/less"] = signal
            dic["<>side"] = right_left
            dic["times what"] = pos_ind[close_pos]
            dic["number"] = number
            dic["comparison"] = neg_ind[close_neg]
            if "times" in sentence.lower():
                where = [pos.start() - numb_ind for pos in re.finditer("times", sentence.lower())]
                for pos in where:
                    if pos < ind and pos > close_pos or pos > ind and pos < close_pos:
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
    check2 = ["<", ">", "<=", ">="]
    number = line[ind]
    new_phrase = " ".join(line)

    if not any(ext in new_phrase for ext in check) and not any(ext in new_phrase for ext in check2):
        return dic

    if any(ext in new_phrase for ext in check):
        if "bigger than" in new_phrase:
            new_phrase = new_phrase.replace("bigger than", "<")
        elif "less than" in new_phrase:
            new_phrase = new_phrase.replace("less than", "<")
    entities = nlp(new_phrase).ents
    new_phrase = new_phrase.split()
    if ind > len(new_phrase):
        return [ ind, new_phrase]
    if new_phrase[ind] != number:
        ind -= 1

    for i in range(-4, 4):
        if ind + i < len(new_phrase) and ind + i >= 0:
            if i > 0:

                if new_phrase[ind + i].lower() in check2:  # INR 1.5 > ULN

                    signal = new_phrase[ind + i]
                    rl_check(new_phrase, number, ind, signal, "right", entities, dic)
            elif i < 0:

                if new_phrase[ind + i].lower() in check2:
                    signal = new_phrase[ind + i]
                    rl_check(new_phrase, number, ind, signal, "left", entities, dic)
    return dic


def print_comp(dic):
    """

    :param dic:
    :return:
    """

    if dic["<>side"] == "left":
        if dic["times"] == None:
            to_print = [dic["comparison"], dic["bigger/less"], dic["number"], dic["times what"]]
        else:
            to_print = [dic["comparison"], dic["bigger/less"], dic["number"], dic["times"], dic["times what"]]
        return " ".join(to_print)

    elif dic["<>side"] == "right":
        if dic["times"] == None:
            to_print = [dic["number"], dic["times what"], dic["bigger/less"], dic["comparison"]]

        else:
            to_print = [dic["number"], dic["times"], dic["times what"], dic["bigger/less"], dic["comparison"]]
        return " ".join(to_print)


def comparison_main(sent, filename):
    sentences = []
    for ind in range(len(sent.split())):
        try:
            if re.findall("\d+", sent.split()[ind]):
                dic = {"filename": filename, "line": sent, "location": "LATER ALLIGATOR", "index": None,
                       "number": None, "unidade": None, "of": None, "comparison": None,
                       "bigger/less": None, "<>side": None, "times": None, "times what": None}
                dic = comparison(sent.split(), ind, dic)
                if dic["comparison"]:
                    dic["index"] = ind
                    dic["number"] = sent.split()[ind]
                    sentences.append(print_comp(dic))
        except:
            pass
    return sentences

