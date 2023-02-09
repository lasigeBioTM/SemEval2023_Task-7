#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to get all ancestors of the annotation from the output file of get_annotations.py
Returns a json file
"""
import pandas as pd
from owlready2 import get_ontology

#------------------------------------------------------------------------------
def json_to_DataFrame(jsonfile):
    """
    

    Parameters
    ----------
    jsonfile : STR
        DESCRIPTION.

    Returns
    -------
    df2 : pd.DataFrame
        DESCRIPTION.

    """
    df=pd.read_json(jsonfile,orient="records",typ='series')
    df2 = pd.DataFrame(df)
    df2.reset_index(level=0, inplace=True)
    df2.columns=["ID","label"]
    df2["ID"]=df2["ID"].apply(lambda x : x.replace(":","_"))
        
    return df2
#------------------------------------------------------------------------------
def load_ontology():
    """
    Loads ontologies on OWL format.
    Returns
    -------
    
    """
    #Human Disease Ontology
    doid = get_ontology("https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/main/src/ontology/doid-merged.owl").load()
    
    #Human Phenotype Ontology
    hp = get_ontology("http://purl.obolibrary.org/obo/hp.owl").load()
    
    #Chemical Entities of Biological Interest
    chebi = get_ontology("http://purl.obolibrary.org/obo/chebi.owl").load()
    
    #Clinical measurement ontology
    cmo = get_ontology("http://purl.obolibrary.org/obo/cmo.owl").load()
    
    #BioAssay Ontology 
    bao = get_ontology("https://raw.githubusercontent.com/BioAssayOntology/BAO/master/bao_complete_merged.owl").load()
    
    #clinical LABoratory Ontology
    labo = get_ontology("http://purl.obolibrary.org/obo/labo.owl").load()
    
    #Ontology of Adverse Events
    oae = get_ontology("https://raw.githubusercontent.com/OAE-ontology/OAE/master/src/oae_merged.owl").load()
                        
                        
    return doid, hp, chebi, cmo, bao, labo, oae

#------------------------------------------------------------------------------
def get_ancestors(iri,ontology):
    """
    Gives IRI ancestors.
    Parameters
    
    ex.ontology_depth_filter("http://purl.obolibrary.org/obo/FMA_45466", fma)
    ----------
    iri : str
        iri of the term.
    ontolgy : str
        Ontology to load.
    Returns
    -------
    int
        Number of ancestors.
    """
    
    iri="http://purl.obolibrary.org/obo/"+iri
    try:
        ancestors = list(ontology.search(iri = iri)[0].ancestors())
    except IndexError:
        ancestors = []
        
    return ancestors

#------------------------------------------------------------------------------
def ancestors_labels(ancestors):
    """
    Buils ID: Label dictionary for all ancestors

    Parameters
    ----------
    ancestors : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    labels =[list(set(x.label)) for x in ancestors]
    ancestors_str=  [str(x) for x in ancestors]
        
    return  dict(zip(ancestors_str, labels))

#------------------------------------------------------------------------------
def main_loop(unique_annotations):
    doid, hp, chebi, cmo, bao, labo, oae = load_ontology()
    
    ancestors=[]
    for r,c in unique_annotations.iterrows():
        if "CHEBI" in c.ID:
            ancestors.append(get_ancestors(c.ID,chebi))
            
        elif "HP" in c.ID:
            ancestors.append(get_ancestors(c.ID,hp))
            
        elif "DOID" in c.ID:
            ancestors.append(get_ancestors(c.ID,doid))
            
        elif "CMO" in c.ID:
            ancestors.append(get_ancestors(c.ID,cmo))
            
        elif "BAO" in c.ID:
            ancestors.append(get_ancestors(c.ID,bao))
            
        elif "LABO" in c.ID:
            ancestors.append(get_ancestors(c.ID,labo))
            
        elif "OAE" in c.ID:
            ancestors.append(get_ancestors(c.ID,oae))
            
        else:
            ancestors.append("NA")
    return ancestors

#------------------------------------------------------------------------------
def main():

    unique_annotations = json_to_DataFrame("../data/unique_annotations.json")
    
    ancestors = main_loop(unique_annotations)
    
    ancestors_label=[]
    for lists in ancestors:
        try:
            ancestors_label.append(ancestors_labels(lists))
        except AttributeError:
            ancestors_label.append("NA")
      
        
    formated_ancestors_label= [{k.strip("obo.").replace("_",":"): v for (k, v) in x.items()} if isinstance(x, dict) else "NA" for x in ancestors_label]
    
    unique_annotations["ancestors"]=formated_ancestors_label
    
    unique_annotations.to_json("../data/ancestors.json",index="orient")
    
#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

    






