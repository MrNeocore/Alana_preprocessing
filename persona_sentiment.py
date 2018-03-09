import json
NEGATIVE_ALL = ['-', '--']
POSITIVE_ALL = ['+', '++']
PERC = 1.0

CONVERT = {"POSITIVE_FEEDBACK":POSITIVE_ALL,
           "NEGATIVE_FEEDBACK":NEGATIVE_ALL,
           "SAD":NEGATIVE_ALL,
           "LOVE":['++'],
           "CONFUSED_FEEDBACK":['-'],
           "ANNOYANCE":["--"],
           "UNKNOWN":["null"]}

def aiml_to_sentiment(data):
    return [(x[0], CONVERT[x[1]]) for x in data]
    
def find_category(sentence, categories):
    sentences = [x[0] for x in categories]
    
    # Done that way so that if sentences turn out to be identical but have different endings, we could still make it work by changing the if test to accept a percentage of error
    for idx, test_sent in enumerate(sentences):
        count = 0
        for w_test, w in zip(test_sent, sentence):
            if w == w_test:
                count += 1
            else: # Only differences at the end of the sentence are allowed
                break
                
        if count > PERC * len(test_sent):
            return categories[idx][1]
            
    # No good enough correspondance found 
    return "UNKNOWN"
    
    
def sentences_to_aiml(in_data, aiml):
    out_data = []

    for out in in_data:
        sentiment = find_category(out, aiml)
        out_data.append((out, sentiment))
        
    return out_data
        
def save(data):
    with open("out.txt", "w") as f:
        f.write("[")
        for x in data:    
            f.write(f"{{'diag':{x[0]}, 'sent':'{x[1]}'}},\n")
        
        f.write("]")
            
if __name__ == "__main__":
    aiml = open("persona.aiml").readlines()
    aiml = list(map(str.strip, aiml))
    aiml = [(x.split("\"")[1], x.split("\"")[3]) for x in aiml]
    in_data = open("persona_outputs.txt").readlines()
    out_data = sentences_to_aiml(in_data, aiml)
    out_data = aiml_to_sentiment(out_data)
    save(out_data)