# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
from spider.process_sql import tokenize, get_sql
from spider.parse_sql_one import get_schemas_from_json, Schema

# %%
jsons = json.load(open('data/spider/tree_trans1.json'))

counts = {
    'all': 0,
    'extra': 0,
    'hard': 0,
    'medium': 0,
    'easy': 0,
}

pref_hardness = 'extra'

# %%
new_samples = []
for (idx, sample) in enumerate(jsons):
    print('[{}] {}'.format(idx, sample['query']))
    if sample['hardness'] != pref_hardness: continue
    counts[sample['hardness']] += 1
    new_samples.append(sample)

# %%
with open('data/spider/tree_trans1_{}.json'.format(pref_hardness), 'w') as f:
    print(json.dumps(new_samples, indent=4), file=f)

# %%
print(counts)

# %%
