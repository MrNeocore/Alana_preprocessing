# Author  : MEYER Jonathan
# Date    : 05/02/2018
# Version : 1.0

import pandas as pd
import sys
from nltk import word_tokenize
from nltk.corpus import stopwords

try:
    from tqdm import tqdm
except ImportError:
	print("Warning : tqdm module not available, the nice little progress bar won't show up :( [Be patient then and don't quit the program]")
	tqdm = lambda x,total : x

PREVIOUS_UTTERANCES_COUNT = 1

def extract_user_utterance(diag):
	usr_utrc = [(idx, x['utterance']) for idx, x in enumerate(diag) if x['actor'] == 'user']
	return [x[0] for x in usr_utrc], [x[1] for x in usr_utrc]

def load_sentiment_list(filename):
	return list(map(str.strip, open(filename).readlines()))

def load_dialogues(filename):
	return pd.read_json("out.json")
	
def filter_diag(diags, sent_words):
	filtered_diags = []
	stop_words = set(stopwords.words('english'))
	for _, convID, diag in tqdm(diags[['conversationID', 'dialogue']].itertuples(), total=len(diags)):	
		n = 1
		idx, diag_f = extract_user_utterance(diag)
		for utrc_num, usr_utrc in zip(idx, diag_f):
			tokenized_filtered = set(word_tokenize(usr_utrc)) - stop_words
			#tokenized_filtered = set(usr_utrc.split(" ")) - stop_words  # More reliable, but slower, probably not worth it

			if (tokenized_filtered.intersection(sent_words)):
				filtered_diags.append({'conversationID':f"{convID}-{n}", "dialogue":diag[max(0,utrc_num-PREVIOUS_UTTERANCES_COUNT):min(utrc_num+1, len(diag))]})
				n += 1
	
	return filtered_diags

def save(diags, filename):
	out_json = pd.DataFrame.from_records(diags).to_json()
	with open(filename, "w") as f:
		f.write(out_json)

def print_usage():
	print("python3 filter.py <INPUT_DATA> <FILTER_WORDS_DATA> <FILTERED_DATA>")

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print_usage()
	diags = load_dialogues(sys.argv[1])
	filters = load_sentiment_list(sys.argv[2])
	filtered_diags = filter_diag(diags, filters)	
	save(filtered_diags, sys.argv[3])
