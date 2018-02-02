# Author  : MEYER Jonathan
# Data    : 02/02/2018
# Version : 1.0

# Note : I 

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
sent = {'0':'neutral', '+':'positive', '-':'negative'}
term_width = 0

pp = pprint.PrettyPrinter(depth=6)

def load(filename):
	
	conversations = []

	print("Loading data")
	data = pd.read_json(filename)

	print("Preparing for annotation")

	for conv in tqdm(data.iterrows(), total=len(data)):
		conversations.append({ 'convID': conv[1]['conversationID'], 
							   'diag': [(trans[turn['actor']],turn['utterance']) for turn in conv[1]['dialogue']],
							   'sent': 'waiting' })
	
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

	while not stop and i < len(convs):
		done = False
		pp.pprint(convs[i])
			
		while not done:
			res = classify()
			
			if res == "q": 	# QUIT
				stop = True
				done = True
		
			elif res == "s": 	# SKIP CURRENT
				print("Skipping conversation")
				del convs[i]
				done = True
	
			else: 				# CONFIRM ANNOTATION 
				confirm = input(f"Confirm '{sent[res]}' sentiment ? ")
				if confirm == "":
					convs[i]['sent'] = res
					count += 1
					done = True
					to_save.append(i)
		i+=1
	
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
	res = input("Type '+', '-' or '0' : ")
	while res not in list(sent.keys()) + ["s", "q"]:
		print("Input a valid sentiment...")
		res = input("Type '+', '-' or '0' : ")

	return res

def disclaimer():
	print("/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\\".center(term_width))
	print("You are about to use a software that is provided for free and has received little testing".center(term_width))
	print("Its author cannot be held responsible for any problem it may cause /!\\".center(term_width))
	print("It is advisable to copy the 'annotations.json' file regularily in order to avoid any large data loss".center(term_width))
	print("\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/\!/".center(term_width))
	
	if input("\nAre you sure you want to use that software ? Type 'yes' :  ") != 'yes':
		print("You didn't accept the terms - exiting")
		exit(1)

def manual():
	print("\n")
	print("\tSoftware 'manual'\n")
	print("Save the sentiment associated with the following discussions using '+' (positive), '-' (negative) or '0' (neutral)")
	print("You can skip a discussion by typing 's'")
	print("You can exit the program by typing 'q'")
	print("Note : You can annotate the data in several chunks, this software should take care of resuming and saving data accordingly\n")
	input("Press a key to continue\n\n")

def intro():
	global term_width
	term_width = int(os.popen('stty size', 'r').read().split()[1])

	print("\n")
	print(f"ALANA annotation {VERSION} [MEYER Jonathan]".center(term_width))
	print("_________________________________________\n".center(term_width))
	disclaimer()
	manual()

if __name__ == "__main__":
	intro()
	file_in = sys.argv[1]
	file_out = sys.argv[2]

	data = load(file_in)
	data = filter_already_annotated(data, file_out)
	data = annotate(data)
	print(f"{len(data)} discussions annotated - Saving...")

	if len(data):
		save(data, file_out)
		print(f"Annotation appended in file {file_out}")

