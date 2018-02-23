# Author  : MEYER Jonathan
# Date    : 23/02/2018
# Version : 1.1

import pandas as pd
import sys
import os
import sklearn.metrics
import pprint as pprint
import annotate

# Unecessary transformation from list -> DF then back to list ?
def to_df(dict_data):
	new_dict = {}
	divergent = pd.DataFrame.from_records(dict_data['div'])
	new_dict['div'] = divergent[divergent['identical'] == False][['convID','diag', 'rnd']]

	new_dict['unknown'] = pd.DataFrame.from_records(dict_data['unknown'])[['convID','diag', 'rnd']] 
	new_dict['ambiguous'] = pd.DataFrame.from_records(dict_data['ambiguous'])[['convID','diag', 'rnd']] 
		
	return new_dict

def print_divergent(div):
	print("\n\n[ANNOTATION DIVERGENCE DETAILS]")
	pd.set_option('display.max_colwidth', int(div.convID.map(len).max()))
	pd.set_option('display.width', 1000)
	pp = pprint.PrettyPrinter(depth=6)
	pp.pprint(div)

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
	results = []
	unknowns = []
	ambiguous = []

	for x in data:
		annotations = list(x[1]['sent'])
		rnd = list(x[1]['rnd'])[0]
	
		# Conversation annotated by 2+ person
		if len(annotations) > 1:
			# None of the annotators skipped this conversation ("unknown")
			if 'u' not in annotations:
				first = annotations[0]
				second = annotations[1]
				annotator1.append(first)
				annotator2.append(second)
				results.append({'convID':x[0], 'diag' : x[1]['diag'].iloc[0][0], 'identical':(first==second), 'annot1':first, 'annot2':second, 'rnd':rnd}) # Rnd required by annotate
				count += 1

				# Conversation flagged ambiguous by any of the annotators 
				if True in list(x[1]['ambiguous']):
					print(f"\t - One of the annotator has flagged the conversation {x[0]} as 'ambiguous'")
					ambiguous.append({'convID':x[0], 'diag' : x[1]['diag'].iloc[0][0], 'identical':(first==second), 'annot1':first, 'annot2':second, 'rnd':rnd})
			
			# Conversation flagged 'unknown' by any of the annotators 			
			else:
				unknowns.append({'convID':x[0], 'diag' : x[1]['diag'].iloc[0][0], 'identical':(first==second), 'annot1':first, 'annot2':second, 'rnd':rnd})
				print(f"\t - One of the annotator has flagged the conversation {x[0]} as 'unknown' - skipping")
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

	return {'div':results, 'unknown':unknowns, 'ambiguous':ambiguous}

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
	results = to_df(results)
	print_divergent(results['div'])
	if input("Do you want to fix now ? (y/n)") == "y":
		fix_annotation(results, in_files)