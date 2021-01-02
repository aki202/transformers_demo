# %%
import re
import json
from pprint import pprint as pp
from nltk import bleu_score, word_tokenize

t5_json = json.load(open('/Users/aki202/Dev/research/transformer/results/t5_sql_to_text.json'))
fp = open('/Users/aki202/Dev/research/sql_to_en/logs/examples/e300_h128_b50_l0.001_E50_1224a.log')
pairs: [{str: str}] = []
index = 0
for line in fp.readlines():
    line = line.rstrip()

    if line.startswith('] '):
        if index <= len(pairs): pairs.append({ 'predicted': '', 'gold': '', 'query': '', 'hardness': '' })
        pairs[index]['query'] = line[2:]
    if line.startswith('= '):
        pairs[index]['gold'] = line[2:]
    if line.startswith('< '):
        pairs[index]['predicted'] = line[2:]
        index += 1
# %%
pairs[0]

# %%
query_to_dict: {str: dict} = {}
for dic in t5_json:
    if 'query' not in dic: continue
    k: str = re.sub('[^a-z]', '', dic['query'].lower())
    query_to_dict[k] = dic

# %%
counts = {
    'all': 0,
    'extra': 0,
    'hard': 0,
    'medium': 0,
    'easy': 0,
}
scores = {
    'all': .0,
    'extra': .0,
    'hard': .0,
    'medium': .0,
    'easy': .0,
}

for (idx, pair) in enumerate(pairs):
    # print(idx, pair, pair['query'])
    k: str = re.sub('[^a-z]', '', pair['query'].lower())
    t5_dic: dict = query_to_dict[k]

    hy = word_tokenize(pair['predicted'])
    go = word_tokenize(pair['gold'])
    blue4 = bleu_score.sentence_bleu([go], hy)

    counts['all'] += 1
    counts[t5_dic['hardness']] += 1
    scores['all'] += blue4
    scores[t5_dic['hardness']] += blue4
    pair['hardness'] = t5_dic['hardness']
    pair['blue'] = blue4

print(counts)

# %%
#print(pairs)
bleus = {}
for (hardness, score) in scores.items():
    print("{} BLEU-4: {}".format(hardness, score / counts[hardness]))
    bleus[hardness] = score / counts[hardness]
pairs.append({ 'bleu': bleus })

# %%
with open('results/lstm_sql_to_text.json', 'w') as f:
    print(json.dumps(pairs, indent=4), file=f)

# %%
