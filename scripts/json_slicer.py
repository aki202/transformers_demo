# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json

# %%
jsons = json.load(open('data/spider/train_others.json'))

# %%
new_samples = []
for (idx, sample) in enumerate(jsons):
    if idx >= 300: break
    print('[{}] {}'.format(idx, sample['query']))
    new_samples.append(sample)

# %%
with open('data/spider/train_others300.json', 'w') as f:
    print(json.dumps(new_samples, indent=4), file=f)

# %%
print(len(new_samples))

# %%
