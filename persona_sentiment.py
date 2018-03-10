import json
import re
NEGATIVE_ALL = ['-', '--']
POSITIVE_ALL = ['+', '++']
PERC = 1.0

CONVERT = {"POSITIVE_FEEDBACK":POSITIVE_ALL,
           "NEGATIVE_FEEDBACK":NEGATIVE_ALL,
           "SAD":NEGATIVE_ALL,
           "LOVE":['++'],
           "CONFUSED_FEEDBACK":['-'],
           "ANNOYANCE":["-"],
           "UNKNOWN":["null"],
           "EMPTY":['0'],
           "INSULT":["--"],
           "PROFANITY":["-"]}
    
def find_category(sentence, categories):
    sentences = [x[0] for x in categories]
    
    for idx, test_sent in enumerate(sentences):
        match = re.match(test_sent, sentence)
        
        if match and len(match.group()) == len(sentence):
            return categories[idx][1]
     
    # No good enough correspondance found 
    return "UNKNOWN"            
    
def sentences_to_aiml(in_data, aiml):
    out_data = []

    for out in in_data:
        category = find_category(out, aiml)
        out_data.append({'diag':out, 'cat':category, 'sent':CONVERT[category]})
        
    return out_data
        
def save(data):
    with open("out.txt", "w") as f:
        f.write("[")
        for x in data:    
            f.write(f"{x}\n") #f"{{'diag':{x[0]}, 'sent':'{x[1]}'}},\n")
        
        f.write("]")
            
if __name__ == "__main__":
    aiml = open("persona.aiml").readlines()
    aiml = list(map(str.strip, aiml))
    aiml = [(x.split("\"")[1], x.split("\"")[3]) for x in aiml]
    in_data = open("persona_outputs.txt").readlines()
    out_data = sentences_to_aiml(in_data, aiml)
    save(out_data)