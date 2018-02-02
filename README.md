# Alana_preprocessing

## Important note : 
  This software is provided as is and hasn't been extensively tested, you have been warned.
  
#### Note : This repository has no (direct) use outside the HW Conversationnal Agent course


## Requirements :
  Linux (bash + sed) [for preprocessing only]
  
  Python 3
    - pandas 
    - tqdm (optional)
  
  
##  How to : 

Given the data from the Alana project, clone this repository and execute the following commands :

### Initial preprocessing : 
```bash
chmod +x preprocessing_alana.sh
./preprocessing_alana.sh <ALANA_RAW_DATA_FILE>
```

If not renamed, the <ALANA_RAW_DATA_FILE> can be "sample_10.json" or "sample_20.json"


### Annotation :
```bash
python3 annotate.py <ALANA_PREPROCESSED_DATA_FILE> <ANNOTATIONS_OUTPUT_FILE>
```

If not renamed, the <ALANA_PREPROCESSED_DATA_FILE> is named "out.json".

The <ANNOTATION_OUTPUT_FILE> argument can also be used to resume annotation (no need to indicate a seperate file everytime)

A "manual" on how to use this script is included in this script itself
