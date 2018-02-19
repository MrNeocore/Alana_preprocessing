# Author  : MEYER Jonathan
# Date    : 19/02/2018
# Version : 1

import pandas as pd
import sys
import os
import sklearn.metrics
import pprint as pprint

def print_results(results):
	print("\n\n[ANNOTATION DIVERGENCE DETAILS]")

	pd.set_option('display.max_colwidth', len(results[0]['convID']))
	pd.set_option('display.width', 1000)

	divergent = pd.DataFrame.from_records(results)
	divergent = divergent[divergent['identical'] == False][['convID', 'annot1', 'annot2']] 
	pp = pprint.PrettyPrinter(depth=6)
	pp.pprint(divergent)

def kappa(data):
	print("\n\n[KAPPA SCORE CALCULATION]\n")

	data = data[['convID', 'sent']]
	data = data.groupby('convID') # Group annotation of the same utterance together
	
	count = 0
	annotator1 = []
	annotator2 = []
	results = []

	for x in data:
		annotations = list(x[1]['sent'])
		if len(annotations) > 1:
			if 'u' not in annotations:
				first = annotations[0]
				second = annotations[1]
				annotator1.append(first)
				annotator2.append(second)
				results.append({'convID':x[0], 'identical':(first==second), 'annot1':first, 'annot2':second})
				count += 1
			else:
				print(f"\t - One of the annotator has flagged the conversation {x['convID']} has 'unknown' - skipping")
		else:
			print(f"\t - Only one annotator for conversation {x[0]}")
	
	# Convert strings into numbers (~hashing) because kappa_score only works on numbers
	annotator1 = [sum([ord(x) for x in y]) for y in annotator1]

	# Avoid bug (??) in kappa_score where if annotator1 == annotator2 and every annotation is identical -> outputs "nan" instead of 1.0
	# Ex : ['s','s','s'] & ['s','s','s']. Should not happend in practice but still...
	annotator1 = [x+n for n, x in enumerate(annotator1)] 

	annotator2 =  [sum([ord(x) for x in y]) for y in annotator2]
	annotator2 = [x+n for n, x in enumerate(annotator2)] 

	print(f"\nScore ==>  {sklearn.metrics.cohen_kappa_score(annotator1, annotator2)} ({count} comparisons)")

	return results

def load_all(in_files):
	print("[LOAD ANNOTATION FILES]\n")
	tmp = []
	
	for f in in_files:
		print(f"\t- {f}")
		tmp.append(pd.read_json(f))

	return pd.concat(tmp, axis=0)

def print_usage():
	print("python3 kappa.py <ANNOTATION_DATA_FOLDER>")

def get_files():	
	if len(sys.argv) < 2:
		print("Missing arguments")
		print_usage()
		exit(1)

	in_folder = sys.argv[1]
	files = []

	if os.path.isdir(in_folder):
		for f in os.listdir(in_folder):
			try:
				pd.read_json(os.path.join(in_folder, f))
			except:
				print(f"Skipping file {f} : Not a valid JSON file")
			else:
				files.append(os.path.join(in_folder, f))

		if len(files):
			return files
		else:
			print(f"No annotation data files found in folder {in_folder}")
			print_usage()
			exit(1)
	else:
		print("Parameter is not a folder")
		print_usage()
		exit(1)



if __name__ == "__main__":
	in_files = get_files()
	data = load_all(in_files)
	print_results(kappa(data))