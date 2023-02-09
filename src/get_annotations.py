#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scritp to get all single pairs of annotation ID:LABEL from the annotated CTR
Returns a json file

"""
import os
import json
import pandas as pd
from os import environ

#------------------------------------------------------------------------------
def annotations_ID_label(annotated_CTR):
    """
    

    Parameters
    ----------
    annotated_CTR : STR
        DESCRIPTION.

    Returns
    -------
    DICT
        DESCRIPTION.

    """

    anno_ctr = pd.read_csv(annotated_CTR,sep="\t")
    
    Id=[]
    labels=[]
    
    for r,c in anno_ctr.iterrows():

        if ":" in c[1]:
            Id.append(c[1])
            labels.append(c[0])
        
    return dict(zip(Id, labels))

#------------------------------------------------------------------------------
def get_annotations_CTR(annotated_CTR_path):
    """
    

    Parameters
    ----------
    annotated_CTR_path : STR
        Dir with annotated CTR files.

    Returns
    -------
    all_annotations : LIST
        List with all annotations per CTR as dict.

    """
   #get all annotations ID:labels from all annotated CTR
    all_annotations= []
    for (dir_path, dir_names, file_names) in os.walk(annotated_CTR_path):
    
            for filename in file_names:
                file=annotated_CTR_path+"/"+filename
                all_annotations.append(annotations_ID_label(file))
    return all_annotations

#------------------------------------------------------------------------------
def split_keys(annotations):
    """
    Split cases were there are more than 1 ID to a label
    Ex.
    {BAO:0010014,UBERON:0000025 : tube}

    Parameters
    ----------
    annotations : DICT
        DESCRIPTION.

    Returns
    -------
    DICT
        DESCRIPTION.

    """
    keys=[]
    values=[]
    
    for k,v in annotations.items():
        if "," in k:
            all_k=k.split(",")
            for kk in all_k:
                keys.append(kk)
                values.append(v)
            
        else:
            keys.append(k)
            values.append(v)
    
    return dict(zip(keys,values))

#------------------------------------------------------------------------------
def main():
    annotated_CTR_path="../data/annotated_data/Annotated_clinical_trial"
    
    all_annotations= get_annotations_CTR(annotated_CTR_path)
    
    #Combine in one single dict with all unique ID:Label pairs
    unique_id_label={k: v for d in all_annotations for k, v in d.items()}
    
    #Remove non single Keys
    clean_unique_id_label =split_keys(unique_id_label)
    
    final=json.dumps(clean_unique_id_label)
    with open("../data/unique_annotations.json", "w") as outfile:
        outfile.write(final)
        
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
 
