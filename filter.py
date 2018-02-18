# Author  : MEYER Jonathan
# Date    : 05/02/2018
# Version : 1.1

import pandas as pd
import sys
from nltk import word_tokenize
from nltk.corpus import stopwords
import random

try:
    from tqdm import tqdm
except ImportError:
	print("Warning : tqdm module not available, the nice little progress bar won't show up :( [Be patient then and don't quit the program]")
	tqdm = lambda x,total : x

PREVIOUS_UTTERANCES_COUNT = 0

def extract_user_utterance(diag):
	usr_utrc = [(idx, x['utterance']) for idx, x in enumerate(diag) if x['actor'] == 'user']
	return [x[0] for x in usr_utrc], [x[1] for x in usr_utrc]

def load_sentiment_list(filename):
	return list(map(str.strip, open(filename).readlines()))

def load_dialogues(filename):
	return pd.read_json(filename)
	
def filter_diag(diags, sent_words):
	print("Adding filtered dialogue turns...")
	filtered_diags = []
	stop_words = set(stopwords.words('english'))
	for _, convID, diag in tqdm(diags[['conversationID', 'dialogue']].itertuples(), total=len(diags)):	
		idx, diag_f = extract_user_utterance(diag)
		for utrc_num, usr_utrc in zip(idx, diag_f):
			tokenized_filtered = set(word_tokenize(usr_utrc)) - stop_words # More reliable, but slower
			#tokenized_filtered = set(usr_utrc.split(" ")) - stop_words  
			
			if tokenized_filtered.intersection(sent_words):
				append_diag(diag, utrc_num, convID, False, filtered_diags)
				
	return filtered_diags

def append_diag(source, raw_num, convID, rnd, dst):
	start_index = max(0,raw_num-PREVIOUS_UTTERANCES_COUNT)
	end_index = min(raw_num+1, len(source))
	sub_convId = f"{convID}-({start_index}-{end_index-1})"
	
	if not rnd or sub_convId not in [x['conversationID'] for x in dst]:
		dst.append({'conversationID': sub_convId, "dialogue":source[start_index:end_index], "rnd":str(rnd)})
		return True
	else:
		return False

def append_random(source, dst, perc_random):
	print("Adding random dialogue turns... ")
	add_count_goal = int(perc_random*len(dst))
	add_count = 0

	with tqdm(total=add_count_goal-1) as pbar:  
		while add_count < add_count_goal:
			pbar.update(add_count - pbar.n)
			convId = source.iloc[random.randint(0, len(source)-1)]['conversationID']
			diag = list(source.loc[source['conversationID'] == convId]['dialogue'])[0]
			idx, diag_f = extract_user_utterance(diag)
			rnd_turn_id = random.randint(0, len(diag_f)-1)
			if (append_diag(diag, idx[rnd_turn_id], convId, True, dst)):
				add_count += 1

def save(diags, filename):
	random.shuffle(diags)
	out_json = pd.DataFrame.from_records(diags).to_json()
	with open(filename, "w") as f:
		f.write(out_json)

def print_usage():
	print("python3 filter.py <INPUT_DATA> <FILTER_WORDS_DATA> <NUM_RANDOM> <FILTERED_DATA>")

def get_params():
	if len(sys.argv) < 5:
		print("Missing arguments")
		print_usage()
		exit(1)
	else:
		try:
			rnd_perc = int(sys.argv[3])
			if rnd_perc <= 0.0:
				exit(1)

		except ValueError:
			print("Values for 'num_split' and / or 'overall' and / or 'num_records' are not integers")
			exit(1)

	return sys.argv[1], sys.argv[2], rnd_perc, sys.argv[4]

if __name__ == "__main__":
	get_params()
	diags = load_dialogues(sys.argv[1])
	filters = load_sentiment_list(sys.argv[2])
	filtered_diags = filter_diag(diags, filters)
	append_random(diags, filtered_diags, int(sys.argv[3])/100)
	save(filtered_diags, sys.argv[4])
