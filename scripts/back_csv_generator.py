# %%
'''
back-translatorの評価
lstm-json, t5-jsonからランダムにCSVを生成
'''
from pprint import pprint as pp
import json
import re
import random
import copy

lstm_json = json.load(open('results/lstm_sql_to_text.json'))
t5_json = json.load(open('results/t5_sql_to_text.json'))
# output = 'results/back_trans_comparison_v2.csv'

def key(s: str) -> str:
    return re.sub(r'[^a-z\d]', '', s.lower())

lstm_json_dict = {}
for j in lstm_json:
    if 'query' not in j: continue
    k = key(j['query'])
    lstm_json_dict[k] = j

# %%
t5_json_levels = {
    'easy': [],
    'medium': [],
    'hard': [],
    'extra': [],
}
results = copy.deepcopy(t5_json_levels)
for j in t5_json:
    if 'query' not in j: continue
    t5_json_levels[j['hardness']].append(j)

#for h in t5_json_levels: print('{}\t{}'.format(h, len(t5_json_levels[h])))

for h in t5_json_levels:
    for t5_j in random.sample(t5_json_levels[h], 10):
        k = key(t5_j['query'])
        results[h].append({
            'lstm': lstm_json_dict[k],
            't5': t5_j,
        })

#pp(results)

# %%
def line(s: str) -> str:
    return re.sub('"', '\\"', s)

for h in results:
    print(h)
    for r in results[h]:
        print('"query","{}"'.format(line(r['lstm']['query'])))
        print('"gold","{}"'.format(line(r['lstm']['gold'])))
        print('"lstm","{}"'.format(line(r['lstm']['predicted'])))
        print('"t5","{}"'.format(line(r['t5']['question'])))
        print('')
    print('')

# %%
