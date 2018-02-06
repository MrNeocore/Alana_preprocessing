import pandas as pd
import sys

def print_usage():
	print("python3 split_dataset.py <ALANA_DATA> <NUM_SPLIT> <OVERLAP_INTEGER_PERC> <RECORDS_PER_FOLD> <OUTPUT_FILE_NAME_ROOT>")

def get_param():
	invalid_conf = False

	if len(sys.argv) < 4:
		invalid_conf = True
		print("Missing arguments")
	
	try:
		num_split = int(sys.argv[2]) 
		overlap = int(sys.argv[3])
		num_records = int(sys.argv[4])
	except ValueError:
		invalid_conf = True
		print("Values for 'num_split' and / or 'overall' and / or 'num_records' are not integers")

	if overlap < 0 or overlap > 99:
		invalid_conf = True
		print("Invalid 'overlap' value")

	if num_split < 0:
		invalid_conf = True
		print("Invalid 'num_split' value")

	if num_records < 0:
		invalid_conf = True
		print("Invalid 'records_per_split' value") # Not covering num_records * num_split > len(data)

	if invalid_conf:
		print_usage()
		exit(1)
	else:
		return sys.argv[1], num_split, overlap, num_records, sys.argv[5]
	

def load_data(filename):
	return pd.read_json(filename)

def split_dataset(data, num_splits, overlap, num_records):
	splits = []
	
	df = pd.DataFrame.from_records(data)
	for idx, split in enumerate(range(num_splits-1)):
		index_h = int(num_records*(idx+1)+overlap/100*num_records)-1
		index_l = int(num_records*idx)
		split_data = df.loc[index_l:index_h]
		splits.append(split_data)

	# Handle last split
	index_h = int(num_records*(idx+2))
	index_l = num_records*(idx+1)	
	split_data = pd.concat([df.loc[index_l:index_h], df.loc[0:int(overlap/100*num_records)]])
	splits.append(split_data)
	

	return splits

def save(data, out_file):
	for idx, split in enumerate(data[:-1]):
		out_filename = f"{out_file}{idx}-{idx+1}.json"
		with open(out_filename, "w") as f:
			f.write(data[idx].to_json())
	
	out_filename = f"{out_file}{len(data)}-0.json"
	with open(out_filename, "w") as f:
		f.write(data[-1].to_json())
	
if __name__ == "__main__":
	in_file, num_splits, overlap, num_records, out_file = get_param()
	in_json = load_data(in_file)
	splits = split_dataset(in_json, num_splits, overlap, num_records)
	save(splits, out_file)