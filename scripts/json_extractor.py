# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
from spider.process_sql import tokenize, get_sql
from spider.parse_sql_one import get_schemas_from_json, Schema

# %%
base = 'tree_trans2'
pref_hardness = ['extra']

jsons = json.load(open('data/spider/{}.json'.format(base)))

counts = {
    'all': 0,
    'extra': 0,
    'hard': 0,
    'medium': 0,
    'easy': 0,
}

# %%
new_samples = []
for (idx, sample) in enumerate(jsons):
    print('[{}] {}'.format(idx, sample['query']))
    if sample['hardness'] not in pref_hardness: continue
    counts[sample['hardness']] += 1
    new_samples.append(sample)

# %%
path = 'data/spider/{}_{}.json'.format(
    base, '_'.join(pref_hardness)
)
with open(path, 'w') as f:
    print(json.dumps(new_samples, indent=4), file=f)

# %%
print(counts)

# %%
