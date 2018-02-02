# Alana data preprocessing Python worker script
# Jonathan Meyer
# V1.1

import pandas as pd
import sys

with open(sys.argv[1], "r") as f:
	in_json = f.read()

in_json = in_json[1:-1]

df = pd.read_json(in_json, lines=True)

out_json = df.to_json(orient='records', lines=True)
out_json = "".join(('[',out_json,']'))


with open("out.json", "w") as f:
    f.write(out_json)