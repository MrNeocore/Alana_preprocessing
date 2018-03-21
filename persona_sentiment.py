import json
import re
NEGATIVE_ALL = ['-', '--']
POSITIVE_ALL = ['+', '++']
PERC = 1.0

CONVERT = {"POSITIVEFEEDBACK":POSITIVE_ALL,
           "NEGATIVEFEEDBACK":NEGATIVE_ALL,
           "SAD":NEGATIVE_ALL,
           "LOVE":['++'],
           "CONFUSEDFEEDBACK":['-'],
           "ANNOYANCE":["-"],
           "OTHER":["0"],
           "EMPTY":['0'], 
           "INSULT":["--"],
           "PROFANITY":["-"],
           "SUICIDE":["--"],
           "LIKEME":POSITIVE_ALL}
    
def find_category(sentence, categories):
    sentences = [x[0] for x in categories]
    
    for idx, test_sent in enumerate(sentences):
        match = re.match(test_sent, sentence)
            
        if match: # Add contraints ? 
            return categories[idx][1]
     
    # No good enough correspondance found 
    return "OTHER"            
    
def sentences_to_aiml(data, aiml):
    for out in data:
        category = find_category(out['answer'], aiml)
        out['cat'] = category
        out['sent_persona'] = CONVERT[category]
        
    return data
        
        
def load_persona_out(filename):
    out = []
    
    with open(filename) as f:
        for x in f.readlines():
            out.append(json.loads(x))
            
    return out

def save(data):
    with open("out.txt", "w") as f:
        for x in data:
            f.write("{}\n".format(json.dumps(x)))
            
if __name__ == "__main__":
    aiml = open("persona.aiml").readlines()
    aiml = list(map(str.strip, aiml))
    aiml = [(x.split("\"")[1], x.split("\"")[3]) for x in aiml]
    in_data = load_persona_out("persona_out.txt")
    out_data = sentences_to_aiml(in_data, aiml)
    save(out_data)