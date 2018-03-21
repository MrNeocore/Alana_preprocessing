sent = {'1':[-3.01, -4.0],
        '2':[-1.0, -3.0], 
        '4':[1.0, 3.0],
        '5':[3.01, 4.0]} 
        
threshold = 2.5

def transform(data):
    out = []
    for x in data:
        for key in list(sent.keys()):
            if abs(float(x[1])) > abs(sent[key][0]) and abs(float(x[1])) <= abs(sent[key][1]) and float(x[1])/abs(float(x[1])) == sent[key][0]/abs(sent[key][0]):
                out.append((x[0], key))
            
    return out
    
    
data = open("vader_lexicon.txt").readlines()
data = list(map(str.strip, data))
data = [(x.split("\t")[0], x.split("\t")[1]) for x in data]

new = []
for x in range(len(data)):
    try:
        tmp = float(data[x][1])
        new.append((data[x][0], tmp))
    except:
        pass
        
data = new 

filt = list(filter(lambda x: abs(float(x[1])) > threshold, data))

final = transform(filt)

pos_count = len([x[1] for x in final if x[1] in ['4', '5']])
neg_count = len([x[1] for x in final if x[1] in ['1', '2']])

with open("dict.txt", "w") as f:
    for x in final:
        f.write(f"{x[0]},{x[1]}\n")