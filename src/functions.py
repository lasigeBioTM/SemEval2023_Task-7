#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import scispacy
import spacy
import pandas as pd
import re

# =============================================================================
def read_json(file):
    f = open(file)
    data = json.load(f)
    f.close()
    return data

# ------------------------------------------------------------------------------
def annotations_to_dict(annotated_CTR_path, identifier):
    """
    Get annotated files from CTR as dictionary.

    Parameters
    ----------
    annotated_CTR_path : STR
        Path for annotated CTR.
    identifier : STR
        CTR ID (eg. identifier='NCT02953860').

    Returns
    -------
    annot_dict : Dict
        Annotations for all sections.

    """
    anno_ctr = pd.read_csv(annotated_CTR_path + identifier + ".tsv", sep="\t")

    counter = 0
    section = ""

    annot_dict = {'Intervention': {}, 'Eligibility': {}, 'Results': {}, 'Adverse Events': {}}

    for r, c in anno_ctr.iterrows():
        if counter == 0:
            section = c[1]
            counter += 1

            sent = "Sentence " + c[2]
            annot_dict[section].update({sent: [c[0]]})

        else:
            if ":" in c[1]:
                annot_dict[section][sent].append(c.to_list())
                counter += 1
            elif c[1] == section:
                sent = "Sentence " + c[2]
                annot_dict[section].update({sent: [c[0]]})
            else:
                section = c[1]
                sent = "Sentence " + c[2]
                annot_dict[section].update({sent: [c[0]]})
                counter += 1

    return annot_dict

# ------------------------------------------------------------------------------
def clean_annotations(annot_dict):
    """
    Clean dictionary with only annotated sentences.

    Parameters
    ----------
    annot_dict : DICT
        Output dict from annotations_to_dict().

    Returns
    -------
    new_annot_dict : DICT
        Dict with only annotated sentences.

    """
    new_annot_dict = {'Intervention': {}, 'Eligibility': {}, 'Results': {}, 'Adverse Events': {}}
    for k in annot_dict.keys():

        for kk in annot_dict[k].keys():
            if len(annot_dict[k][kk]) > 1:

                new_annot_dict[k].update({kk: annot_dict[k][kk]})
            else:
                pass
    return new_annot_dict

# ------------------------------------------------------------------------------
def score_label_spacy(score):
    """
    Gives final label prediction.

    Parameters
    ----------
    score : FLOAT
        similarity score.

    Returns
    -------
    Prediction : INT
        1:Entailment; 0:Contradiction.

    """

    if score > 0.5:  # contradiction
        prediction = 0
        label = " Contradiction"

    else:  # "Entailment"
        prediction = 1
        label = "Entailment"

    return prediction, label

# ------------------------------------------------------------------------------
def clean(text):
    """
    Normalize annotations in a single text

    Parameters
    ----------
    text : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """

    text = re.sub(r'\W+', ' ', text)  # remove non-alphanumeric characters

    text = text.lower()  # lower case everything
    return text.strip()  # remove redundant spaces

# ------------------------------------------------------------------------------
def ancestors_df(jsonfile):
    # jsonfile= "../data/ancestors.json"

    df = pd.read_json(jsonfile, orient="records")

    # Delete entries without ancestors
    dataset = df.loc[df['ancestors'] != "NA"]

    return dataset

# ------------------------------------------------------------------------------
def annotations_with_ancestors_to_dict(annotated_CTR_path, identifier, dataset):
    """
    Get annotated files from CTR as dictionary and match IDs with ancestors.

    Parameters
    ----------
    annotated_CTR_path : STR
        Path for annotated CTR.
    identifier : STR
        CTR ID (eg. identifier='NCT02953860').
    ancestors : pd.DataFrame
        ancestors info.

    Returns
    -------
    annot_dict : Dict
        Annotations for all sections.

    """

    anno_ctr = pd.read_csv(annotated_CTR_path + identifier + ".tsv", sep="\t")
    counter = 0
    section = ""

    annot_dict = {'Intervention': {}, 'Eligibility': {}, 'Results': {}, 'Adverse Events': {}}

    for r, c in anno_ctr.iterrows():
        if counter == 0:
            section = c[1]
            counter += 1

            sent = "Sentence " + c[2]
            annot_dict[section].update({sent: [c[0]]})


        else:
            if ":" in c[1]:

                a = c[1].replace(":", "_")
                ancestors = dataset.loc[dataset['ID'] == a]["ancestors"].to_list()
                if len(ancestors) != 0:
                    c = c.to_list()
                    c.append(ancestors)
                    annot_dict[section][sent].append(c)
                else:
                    annot_dict[section][sent].append(c.to_list())
                counter += 1
            elif c[1] == section:
                sent = "Sentence " + c[2]
                annot_dict[section].update({sent: [c[0]]})
            else:
                section = c[1]
                sent = "Sentence " + c[2]
                annot_dict[section].update({sent: [c[0]]})
                counter += 1
    return annot_dict

# ------------------------------------------------------------------------------



