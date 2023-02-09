#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from comparison import *
from units import *
from functions import *

from collections import ChainMap
import scispacy

from sklearn.metrics import f1_score, precision_score, recall_score
import networkx as nx
import itertools
import copy

import sys
import os
import re
# =============================================================================

nlp = spacy.load("en_core_sci_lg")


def insert_sdp_cdr(section_annotations):
    """

    :param section_annotations:
    :return:
    """

    sentences = copy.deepcopy(section_annotations)

    for sentence_id, sentence_descriptors in sentences.items():
        if len(sentence_descriptors) > 2:
            entities = sentence_descriptors[1:]

            combinations_entities = list(itertools.combinations(entities, 2))

            for combination in combinations_entities:
                if combination[0][0] != combination[1][0]:
                    entity_1 = re.sub(r'\s+', '_', combination[0][0]).lower()
                    entity_2 = re.sub(r'\s+', '_', combination[1][0]).lower()

                    sentence = sentence_descriptors[0].lower()
                    sentence = sentence.replace(combination[0][0], entity_1).replace(combination[1][0], entity_2)

                    doc = nlp(sentence)
                    sdp = get_shortest_dependency_path(doc, entity_1, entity_2)

                    if sdp not in section_annotations[sentence_id]:
                        section_annotations[sentence_id].append(sdp)

    return section_annotations

# ------------------------------------------------------------------------------
def insert_sdp_hyp(section_annotations):
    """

    :param section_annotations:
    :return:
    """

    sentences = copy.deepcopy(section_annotations)

    for sentence in sentences:
        if len(sentences) > 2:
            entities = sentences[1:]

            combinations_entities = list(itertools.combinations(entities, 2))

            for combination in combinations_entities:
                if combination[0][0] != combination[1][0]:
                    entity_1 = re.sub(r'\s+', '_', combination[0][0]).lower()
                    entity_2 = re.sub(r'\s+', '_', combination[1][0]).lower()

                    sentence = sentences[0].lower()
                    sentence = sentence.replace(combination[0][0], entity_1).replace(combination[1][0], entity_2)

                    doc = nlp(sentence)
                    sdp = get_shortest_dependency_path(doc, entity_1, entity_2)

                    if sdp not in section_annotations:
                        section_annotations.append(sdp)

    return section_annotations

# ------------------------------------------------------------------------------
def get_shortest_dependency_path(doc, entity_1, entity_2):
    """

    :param doc:
    :param entity_1:
    :param entity_2:
    :return:
    """

    try:
        edges = []
        for token in doc:
            for child in token.children:
                edges.append(('{0}'.format(token.lower_), '{0}'.format(child.lower_)))

        graph = nx.Graph(edges)
        return nx.shortest_path(graph, source=entity_1, target=entity_2)

    except nx.exception.NodeNotFound:  # sometimes due to ( or ) next to text, e.g., receptor(egfr
        pass

    except nx.exception.NetworkXNoPath:
        pass

# ------------------------------------------------------------------------------
def get_units(id_, ctr):
    """

    :param id_:
    :param ctr:
    :return:
    """

    sentences = []
    for key in ctr:
        for sent in ctr[key]:
            uni = unidades_main(sent)
            if uni != {} and str(uni) != "None":
                pass
            sentences.append(comparison_main(sent, id_[1]))

            if sentences:
                pass

    return sentences

# ------------------------------------------------------------------------------
def insert_units(section_annotations_sdp, sentences):
    """

    :param section_annotations_sdp:
    :param sentences:
    :return:
    """

    for sentence_id, sentence_descriptors in section_annotations_sdp.items():
        for sentence in sentences:
            if sentence and sentence not in section_annotations_sdp[sentence_id]:
                section_annotations_sdp[sentence_id].append(sentence)

    return section_annotations_sdp

# ------------------------------------------------------------------------------
# SECTION
def get_section(id_, hyp_doc, sentences, annotations_dict, section, results_pred, main_info):
    """

    :param id_:
    :param hyp_doc:
    :param annotations_dict:
    :param section:
    :param results_pred:
    :param main_info:
    :return:
    """

    try:
        section_annotations = annotations_dict[section]
        section_annotations_sdp = insert_sdp_cdr(section_annotations)
        section_annotations_sdp_units = insert_units(section_annotations_sdp, sentences)
        annot_text = json.dumps(section_annotations_sdp_units)  # to str
        X_p = nlp(annot_text)

        score = hyp_doc.similarity(X_p)
        results_pred.append(score_label_spacy(score)[0])
        main_info.append({id_[0]: {"Prediction": score_label_spacy(score)[1]}})

    except ValueError:
        pass

    return results_pred, main_info

# ------------------------------------------------------------------------------
# ANNOTATIONS HYPOTHESIS
def get_annotations_hypothesis(annotated_hypothesis_file):
    """

    :param annotated_hypothesis_file:
    :return:
    """

    anno_hyp = pd.read_csv(annotated_hypothesis_file, sep="\t", names=[0, 1, 2])

    annotations_dict_hyp = {}
    save_sentence = ''
    for r, c in anno_hyp.iterrows():
        if c[0].count('-') == 4:
            annotations_dict_hyp[c[1]] = []
            save_sentence = c[1]
        elif len(c) == 3:
            annotations_dict_hyp[save_sentence].append([c[0], c[1], c[2]])

    return annotations_dict_hyp

# ------------------------------------------------------------------------------
def get_info_no_secondary_id(ancestors_dataframe,hyp_doc, annotated_CTR_path, id_, base_path_CTR, section, gold_labels, results_pred, main_info, hypothesis_text, fn_fe, inter, eli, res, adv):
    """

    :param hyp_doc:
    :param annotated_CTR_path:
    :param id_:
    :param base_path_CTR:
    :param section:
    :param gold_labels:
    :param results_pred:
    :param main_info:
    :param hypothesis_text:
    :param fn_fe:
    :param inter:
    :param eli:
    :param res:
    :param adv:
    :return:
    """

    try:
        annotations_dict = clean_annotations(annotations_with_ancestors_to_dict(annotated_CTR_path, id_[1]["Primary_id"],ancestors_dataframe))

        ctr = read_json(base_path_CTR + id_[1]["Primary_id"] + ".json")

        sentences = get_units(id_, ctr)

        try:
            if id_[1]['Label'] == 'Contradiction':
                gold_labels.append(0)
            else:
                gold_labels.append(1)
        except KeyError:
            gold_labels.append(1)

        results_pred_out, main_info_out = get_section(id_, hyp_doc, sentences, annotations_dict, section, results_pred, main_info)
        results_pred, main_info = results_pred_out, main_info_out

    except FileNotFoundError:
        fn_fe += 1

    return results_pred, main_info, gold_labels, fn_fe, inter, eli, res, adv

# ------------------------------------------------------------------------------
def join_annotations(primary_dict, secondary_dict):
    """

    :param primary_dict:
    :param secondary_dict:
    :return:
    """

    counter = 0
    joined_dict = {}
    for sentence_id, elements in primary_dict.items():
        joined_dict[str(counter)] = elements
        counter += 1

    for sentence_id, elements in secondary_dict.items():
        joined_dict[str(counter)] = elements
        counter += 1

    return joined_dict

# ------------------------------------------------------------------------------
def get_info_secondary_id(ancestors_dataframe,hyp_doc, annotated_CTR_path, base_path_CTR, section, id_, results_pred, main_info, gold_labels, fn_fe):
    """

    :param hyp_doc:
    :param annotated_CTR_path:
    :param base_path_CTR:
    :param section:
    :param id_:
    :param results_pred:
    :param main_info:
    :param gold_labels:
    :param fn_fe:
    :return:
    """

    try:
        ctr_primary = read_json(base_path_CTR + id_[1]["Primary_id"] + ".json")
        sentences_primary = get_units(id_, ctr_primary)

        ctr_secondary = read_json(base_path_CTR + id_[1]["Secondary_id"] + ".json")
        sentences_secondary = get_units(id_, ctr_secondary)

        sentences = sentences_primary + sentences_secondary

        try:
            # annotations_dict_primary = clean_annotations(annotations_to_dict(annotated_CTR_path, id_[1]["Primary_id"]))
            # annotations_dict_secondary = clean_annotations(annotations_to_dict(annotated_CTR_path, id_[1]["Secondary_id"]))

            #ancestors
            annotations_dict_primary = clean_annotations(annotations_with_ancestors_to_dict(annotated_CTR_path, id_[1]["Primary_id"],ancestors_dataframe))
            annotations_dict_secondary = clean_annotations(annotations_with_ancestors_to_dict(annotated_CTR_path, id_[1]["Secondary_id"],ancestors_dataframe))


        except pd.errors.ParserError:
            print(id_[1])

        section_annotations_primary = annotations_dict_primary[section]
        section_annotations_secondary = annotations_dict_secondary[section]

        section_annotations = join_annotations(section_annotations_primary, section_annotations_secondary)
        section_annotations_sdp = insert_sdp_cdr(section_annotations)
        section_annotations_sdp_units = insert_units(section_annotations_sdp, sentences)
        combo_text = json.dumps(section_annotations_sdp_units)  # to str
        X_p = nlp(combo_text)
        score = hyp_doc.similarity(X_p)

        results_pred.append(score_label_spacy(score)[0])
        main_info.append({id_[0]: {"Prediction": score_label_spacy(score)[1]}})

        try:
            if id_[1]['Label'] == 'Contradiction':
                gold_labels.append(0)
            else:
                gold_labels.append(1)
        except KeyError:
            gold_labels.append(1)

    except FileNotFoundError:
        fn_fe += 1

    return results_pred, main_info, gold_labels, fn_fe

# ------------------------------------------------------------------------------
def get_main_info(hypothesis_path, base_path_CTR, annotated_CTR_path, annotated_hypothesis_file,ancestors_json):
    """

    :param hypothesis_path:
    :param base_path_CTR:
    :param annotated_CTR_path:
    :param annotated_hypothesis_file:
    :return:
    """

    all_hypothesis = read_json(hypothesis_path)
    annotations_dict_hyp = get_annotations_hypothesis(annotated_hypothesis_file)
    ancestors_dataframe= ancestors_df(ancestors_json)

    single, comparison, fn_fe = 0, 0, 0
    inter, eli, res, adv = 0, 0, 0, 0

    results_pred_final = []
    gold_labels_final = []
    main_info_final = []

    for id_ in all_hypothesis.items():

        hypothesis_text = id_[1]["Statement"]

        hyp_doc = nlp(hypothesis_text)
        section = id_[1]["Section_id"]

        if "Secondary_id" not in id_[1].keys():
            single += 1
            results_pred_out, main_info_out, gold_labels_out, fn_fe, inter, eli, res, \
                adv = get_info_no_secondary_id(ancestors_dataframe,hyp_doc, annotated_CTR_path, id_, base_path_CTR, section, gold_labels_final,
                                               results_pred_final, main_info_final, hypothesis_text, fn_fe, inter, eli, res, adv)

            results_pred_final, gold_labels_final, main_info_final = results_pred_out, gold_labels_out, main_info_out

        else:
            comparison += 1
            results_pred_out, main_info_out, gold_labels_out, \
                fn_fe = get_info_secondary_id(ancestors_dataframe,hyp_doc, annotated_CTR_path, base_path_CTR, section, id_, results_pred_final, main_info_final, gold_labels_final, fn_fe)

            results_pred_final, gold_labels_final, main_info_final = results_pred_out, gold_labels_out, main_info_out

    return results_pred_final, main_info_final, gold_labels_final

# ------------------------------------------------------------------------------
def get_final_results(results_pred, main_info, gold_labels):
    """

    :param results_pred:
    :param main_info:
    :param gold_labels:
    :return:
    """

    main_dict = dict(ChainMap(*main_info))

    d = json.dumps(main_dict, indent=4)

    with open("results_C_20230131.json", "w") as outfile:
        outfile.write(d)

    f_score = f1_score(gold_labels, results_pred)
    p_score = precision_score(gold_labels, results_pred)
    r_score = recall_score(gold_labels, results_pred)

    print('F1:{:f}'.format(f_score))
    print('precision_score:{:f}'.format(p_score))
    print('recall_score:{:f}'.format(r_score))

# ------------------------------------------------------------------------------
def main():
    """Usage example:

    python3 parser_pedro.py

    :return:
    """

    set= str(sys.argv[1])
    # PATHS
    annotated_CTR_path = "../data/annotated_data/Annotated_clinical_trial/"
    base_path_CTR = "../data/Complete_dataset/CT json/"
    ancestors_json = "../data/ancestors.json"
    # =============================================================================
    # PATHS DEV
    if set == "dev":
        print("Dev")
        hypothesis_path = "../data/Complete_dataset/dev.json"
        annotated_hypothesis_file = "../data/annotated_data/dev_ner.tsv"
    # =============================================================================

    # =============================================================================
    # PATHS TEST
    else:
        print("Test")
        hypothesis_path = "../data/Complete_dataset/test.json"
        annotated_hypothesis_file = "../data/annotated_data/test_ner.tsv"
    # =============================================================================

    results_pred, main_info, gold_labels = get_main_info(hypothesis_path, base_path_CTR, annotated_CTR_path, annotated_hypothesis_file,ancestors_json)
    get_final_results(results_pred, main_info, gold_labels)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
