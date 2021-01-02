# %%
from pprint import pprint as pp
import sys
import json

q = sys.argv[1]
jsons = json.load(open('data/spider/train_all.json'))

print(q)
for (idx, sample) in enumerate(jsons):
    if q in sample['query']:
        print('{}: {}'.format(idx, sample['query']))
