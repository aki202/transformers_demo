# %%
import json

# %%
base = 'tree_trans2'
pref_hardness = ['hard', 'extra']

jsons = json.load(open('data/spider/tree_trans2.json'))

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
    if sample['hardness'] not in pref_hardness: continue
    counts[sample['hardness']] += 1
    print('[{}][{}]'.format(idx, sample['hardness']))
    print(sample['query'])
    print(sample['question'])
    print()

print(counts)

# %%
