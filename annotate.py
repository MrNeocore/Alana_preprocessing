# Author  : MEYER Jonathan
# Date    : 19/02/2018
# Version : 1.02.1

import pandas as pd
import pprint as pprint
import json
import sys
import os

try:
    from tqdm import tqdm
except ImportError:
	print("Warning : tqdm module not available, the nice little progress bar won't show up :(")
	tqdm = lambda x,total : x


VERSION = "1.0"
trans = {'user':'U', 'system':'S' }
sents = {'0':'neutral', '+':'positive', '++':'very positive', '-':'negative', '--':'very negative', 's':'null', 'u':'unknown'}
extra_keys = ['q'] # ,'s']

term_width = 0

pp = pprint.PrettyPrinter(depth=6)

def load(filename):
	
	conversations = []

	print("Loading data")
	data = pd.read_json(filename)

	print("Preparing for annotation")

	try:
		for conv in tqdm(data.iterrows(), total=len(data)):
			#import pdb;pdb.set_trace()
			conversations.append({ 'convID': conv[1]['conversationID'], 
								   'diag': [(trans[turn['actor']],turn['utterance']) for turn in conv[1]['dialogue']],
								   'rnd': conv[1]['rnd'],
								   'sent': 'waiting' })
	except Exception as e:
		print(e)
		import pdb; pdb.set_trace()

	print("\nReady to annotate")

	return conversations


# Prevent re-annotation of already annotated dialogues
def filter_already_annotated(data, filename):
	convs_done = []
	
	try:
		with open(filename, "r") as f:
			already = json.load(f)
		
		already_ids = [x['convID'] for x in already]
		data = [x for x in data if x['convID'] not in already_ids]
	
	except FileNotFoundError:
		print(f"No previous annotations found in file {filename}")

	else:
		print(f"Previous annotation file {filename} detected - {len(already_ids)} discussion already annotated")

	if len(data):
		print(f"{len(data)} conversations to annotate\n")

	return data



def annotate(convs): 

	if len(convs) == 0:
		print("No conversations to annotate - exiting")

	annotations = []
	to_save = []
	
	res = ""
	count = 0
	stop = False
	i = 0

	try:
		while not stop and i < len(convs):
			done = False
			pp.pprint({'convID':convs[i]['convID'], 'diag': convs[i]['diag'], 'rnd': convs[i]['rnd']})
				
			while not done:
				res = classify()
				
				if res == "q": 	# QUIT
					stop = True
					done = True
			
				#elif res == "s": 	# SKIP CURRENT
				#	print("Skipping conversation")
				#	del convs[i]
				#	done = True
		
				else: 				# CONFIRM ANNOTATION 
					confirm = input(f"Confirm '{sents[res]}' sentiment ? ")
					if confirm == "":
						convs[i]['sent'] = res
						count += 1
						done = True
						to_save.append(i)
			i+=1
			print("\n")
	
	except (KeyboardInterrupt, EOFError): # Catch Ctrl-C & Ctrl-D
		done = True
		stop = True
	
	convs = [convs[j] for j in to_save]

	return convs



def save(json_data, filename):
	
	try:
		with open(filename, "r") as f:
			previous = json.load(f) # Data already present annotated
			json_data.extend(previous)
	except:
		pass

	json.dump(json_data, open(filename, "w"), indent=4, sort_keys=True)



# Handle part of the user input
def classify():
	res = input(f"Type {list(sents.keys())+extra_keys} : ")
	while res not in list(sents.keys()) + extra_keys:
		print("Input a valid sentiment...")
		res = input(f"Type {list(sents.keys())+extra_keys} : ")

	return res

def disclaimer():
	print("/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\\".center(term_width))
	print("You are about to use a software that is provided for free and has received little testing".center(term_width))
	print("Its author cannot be held responsible for any problem it may cause".center(term_width))
	print("It is advisable to copy the 'annotations.json' file regularily in order to avoid any large data loss".center(term_width))
	print("\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/".center(term_width))
	
	if input("\nAre you sure you want to use that software ? Type 'yes' :  ") != 'yes':
		print("You didn't accept the terms - exiting")
		exit(1)

def sents_to_str():
	txt = "\n"
	for key, sent in sents.items():
		txt += f"\t{key} ({sent})\n"
	
	return txt

def manual():
	print("\n")
	print("\tSoftware 'manual'\n")
	print(f"Save the sentiment associated with the following discussions using : {sents_to_str()}.")
	#print("You can skip a discussion by typing 's'.")
	print("You can indicate that the dialogue turn is 'irrelevant' ('null' sentiment) by typing 's'.")
	print("You can flag a dialogue turn with the 'sentiment' 'u' (unknown) when you aren't sure which sentiment this should be associated.")
	print("You can exit the program by typing 'q'.")
	print("Note : You can annotate the data in several chunks, this software should take care of resuming and saving data accordingly.\n")
	input("Press a key to continue.\n\n")

def intro():
	global term_width
	term_width = int(os.popen('stty size', 'r').read().split()[1])

	print("\n")
	print(f"ALANA annotation {VERSION} [MEYER Jonathan]".center(term_width))
	print("_________________________________________\n".center(term_width))
	disclaimer()
	manual()

def print_usage():
	print("python3 annotate.py <ALANA_DATA_FILE> <OUTPUT_DATA_FILE>")

def get_params():
	if len(sys.argv) < 3:
		print("Missing arguments")
		print_usage()
		exit(1)

	in_file = sys.argv[1]
	out_file = sys.argv[2]
	
	try:
		pd.read_json(in_file)
	except:
		print("Input file doesn't exists or is invalid")
		exit(1)
	else:
		return in_file, out_file

if __name__ == "__main__":
	in_file, out_file = get_params()
	intro()
	data = load(in_file)
	data = filter_already_annotated(data, out_file)
	data = annotate(data)
	print(f"\n{len(data)} discussions annotated - Saving...")

	if len(data):
		save(data, out_file)
		print(f"Annotation appended in file {file_out}")

