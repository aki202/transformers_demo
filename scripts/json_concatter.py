# %%
'''
Concat two json files into one json file
'''
from pprint import pprint as pp
import json

base = 'tree_trans2'
level = 'extra'
jsons1 = json.load(open('data/spider/train_all.json'))
jsons2 = json.load(open('data/spider/{}_{}.json'.format(
    base, level
)))
output = 'data/spider/train_all_cat_{}_{}.json'.format(
    base, level
)

samples = []

def append_to_samples(jsons: [dict]) -> None:
    for (idx, sample) in enumerate(jsons):
        print('[{}] {}'.format(idx, sample['query']))
        samples.append(sample)

# %%
append_to_samples(jsons1)
append_to_samples(jsons2)

with open(output, 'w') as f:
    print(json.dumps(samples, indent=4), file=f)

# %%
