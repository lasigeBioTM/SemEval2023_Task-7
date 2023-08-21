# lasigeBioTM @ SemEval 2023 Task 7: Multi-evidence Natural Language Inference for Clinical Trial Data (NLI4CT) Subtask 1

The present repository contains the data used for our participation at the SemEval 2023 Task 7 Subtask 1.

The academic paper describing our participation (user *dpavot*) in SemEval 2023 Task 7 will be available [here](https://aclanthology.org/2023.semeval-1.2/).


## Dependencies

* requirements.txt

* Python >= 3.10.6

## Workflow
* Annotated files available at *data/annotated_data*

* CTR Ancestors Pre-processing:
    ````
    * src/get_annotations.py
    * src/ontology_ancestors.py
    ````

* Main Pipeline:
    ````
    * src/main_parser.py
    ````
    * Run:
        ````
        * main_parser.py dev
        * main_parser.py test
        ````
        
    
