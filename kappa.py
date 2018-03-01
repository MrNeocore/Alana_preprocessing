# Author  : MEYER Jonathan
# Date    : 01/03/2018
# Version : 1.2

import pandas as pd
import sys
import os
import sklearn.metrics
import pprint as pprint
import annotate
#import debug

AMBIGUOUS_OK = True
SKIPPED_OK = False
UNKNOWN_OK = False	

def print_divergent(div):
	print("\n\n[ANNOTATION DIVERGENCE DETAILS]")
	pd.set_option('display.max_colwidth', int(div.convID.map(len).max())+1)
	pd.set_option('display.width', 1000)
	pd.set_option('display.max_rows',500)

	pp = pprint.PrettyPrinter(depth=6)
	pp.pprint(div[['convID','diag', 'annot1', 'annot2']])
	print(f"{len(div)} turns")
	
def fix_annotation(data, files):
	combined = pd.concat(list(data.values()))
	combined = combined.drop_duplicates(subset='convID')
	combined = list(combined.T.to_dict().values())

	print("\n")
	annotations = annotate.annotate(combined)

	if len(annotations):
		print(f"\n{len(annotations)} discussions annotated - Saving...")
		out_file = input("Please enter an output filename : ")
		out_file = "/".join(files[0].split('/')[:-1]) + "/" + "CORRECTED_" + out_file + ".json"
		annotate.save(annotations, out_file)
		print(f"Annotation appended in file {out_file}")


def kappa(data):
	print("\n\n[KAPPA SCORE CALCULATION]\n")

	data = data[['convID', 'sent', 'diag', 'ambiguous', 'rnd']]
	data = data.groupby('convID') # Group annotation of the same utterance together
	
	count = 0
	annotator1 = []
	annotator2 = []

	div = []
	unknowns = []
	ambiguous = []
	good = []
	skipped = []
	a = []

	for x in data:
		annotations = list(x[1]['sent'])
		rnd = list(x[1]['rnd'])[0] == 'True'
		multi_annotator = len(annotations) > 1
		unknown_flag = 'u' in annotations
		skipped_flag = 's' in annotations
		ambiguous_flag = True in list(x[1]['ambiguous'])
		
		first = annotations[0]
		
		record = {'convID':x[0], 'diag' : x[1]['diag'].iloc[0][0], 'rnd':rnd, 'ambiguous':ambiguous_flag, 'multi':False, 'identical':True, 'annot1':first, 'annot2':"", 'unknown':unknown_flag, 'skipped':skipped_flag}

		if multi_annotator:
			second = annotations[1]
			same_annot = first == second
			record.update({'identical': same_annot, 'annot2': second, 'multi':True})	
				
			if not unknown_flag:
				annotator1.append(first)
				annotator2.append(second)
				count += 1

		a.append(record)

	a = pd.DataFrame.from_records(a)
	div = a.loc[(a['identical'] == False) & (a['unknown'] == False)]
	unknowns = a.loc[a['unknown'] == True]
	ambiguous = a.loc[a['ambiguous'] == True]
	skipped = a.loc[a['skipped'] == True]	

	good = a.loc[a['identical'] == True]

	if not UNKNOWN_OK:
		good = good.loc[good['unknown'] == False]
	if not AMBIGUOUS_OK:
		good = good.loc[good['ambiguous'] == False]
	if not SKIPPED_OK:
		good = good.loc[good['skipped'] == False]			

	# Convert strings into numbers (~hashing) because kappa_score only works on numbers
	annotator1 = [sum([ord(x) for x in y]) for y in annotator1]

	# Avoid bug (??) in kappa_score where if annotator1 == annotator2 and every annotation is identical -> outputs "nan" instead of 1.0
	# Ex : ['s','s','s'] & ['s','s','s']. Should not happend in practice but still...
	annotator1 = [x+n for n, x in enumerate(annotator1)] 

	annotator2 =  [sum([ord(x) for x in y]) for y in annotator2]
	annotator2 = [x+n for n, x in enumerate(annotator2)] 

	print(f"Score ==>  {sklearn.metrics.cohen_kappa_score(annotator1, annotator2)} ({count} comparisons)")

	return {'div':div, 'unknown':unknowns, 'ambiguous':ambiguous, 'good':good, 'skipped':skipped}

def save_good(good):
	good = good.drop_duplicates(subset='convID')
	good['sent'] = good['annot1']
	good = good.drop('annot1', axis=1)
	good = good.drop('annot2', axis=1)
	good = good.drop('identical', axis=1)

	good = list(good.T.to_dict().values())
	
	annotate.save(good, "combined_good.json")

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
	results = kappa(data)
	#results = to_df(results)
	print_divergent(results['div'])
	save_good(results['good'])
	if input("Do you want to fix now ? (y/n)") == "y":
		fix_annotation(results, in_files)