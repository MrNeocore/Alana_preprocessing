# Alana_preprocessing

## Important note : 
  This software is provided as is and hasn't been extensively tested, you have been warned.
  
#### Note : This repository has no (direct) use outside the HW Conversationnal Agent course


## Requirements :
  * Linux (bash + sed) [preprocessing only]
  
  * Python 3
     * pandas
     * tqdm (optional)
     * nltk [filtering step only]
     
  * Alana JSON data
     
  
  
##  How to : 

Clone this repository and execute the following commands :

<ALANA_DATA_FILE> can be either the original or the preprocessed data (named "out.json" by default)


### Filtering :
The goal is to extract part of the discussions worth annotating

For now, it is simply checking if user's utterances contain words likely to convey an emotion

The database used is "Liu and Hu opinion lexicon" (for reference -> https://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html#lexicon)

```bash
python3 filter.py <ALANA_DATA_FILE> <FILTER_WORDS_DATA_FILE> <FILTERED_DATA_OUTPUT_FILE>
```

The <FILTER_WORDS_DATA_FILES> is a text file with a single word on every line. If any of those words is found in an user's utterance, the dialogue turn is saved to the output file


### (Optional) Split dataset into smaller datasets for group annotation

```bash
python3 split_dataset.py <ALANA_DATA_FILE> <NUM_SPLIT> <OVERLAP_INTEGER_PERC> <RECORDS_PER_FOLD> <OUTPUT_FILE_NAME_ROOT>
```

<NUM_SPLIT> : Number of smaller datasets of size <RECORDS_PER_FOLD> to create

<OVERLAP_INTEGER_PERC> : Percentage (0-100, integer) of overlap between datasets

<OUTPUT_FILE_NAME_ROOT> : Output files base name
Ex : "dataset" -> [dataset0-1.json, dataset1-2.json, dataset2-0.json]


### Annotation :
```bash
python3 annotate.py <ALANA_PREPROCESSED_DATA_FILE> <ANNOTATIONS_OUTPUT_FILE>
```

If not renamed, the <ALANA_PREPROCESSED_DATA_FILE> is named "out.json"

The <ANNOTATION_OUTPUT_FILE> argument can also be used to resume annotation (no need to indicate a seperate file everytime)

A "manual" on how to use this script is included in this script itself


### (Optional) Data processing to make the data human readable from a text editor : 
```bash
chmod +x preprocessing_alana.sh
./preprocessing_alana.sh <ALANA_RAW_DATA_FILE>
```

If not renamed, the <ALANA_RAW_DATA_FILE> can be "sample_10.json" or "sample_20.json".
