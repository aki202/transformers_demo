# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
from spider.process_sql import tokenize, get_sql
from spider.parse_sql_one import get_schemas_from_json, Schema
import math

# %%
base = sys.argv[1] # train_all
pref_hardness = ['easy', 'medium', 'hard', 'extra']

jsons = json.load(open('data/spider/{}.json'.format(base)))

counts = {
    'all': 0,
    'extra': 0,
    'hard': 0,
    'medium': 0,
    'easy': 0,
}

max_counts = {
    'easy': math.floor(1989 * 0.8),
    'medium': math.floor(3875 * 0.8),
    'hard': math.floor(1467 * 0.8),
    'extra': math.floor(1328 * 0.8),
}

# %%
new_samples = []
for (idx, sample) in enumerate(jsons):
    print('[{}] {}'.format(idx, sample['query']))
    if sample['hardness'] not in pref_hardness: continue
    if counts[sample['hardness']] >= max_counts[sample['hardness']]: continue
    counts['all'] += 1
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
