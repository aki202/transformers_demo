# %%
'''
Count data in the json file for each haedness
'''
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from pprint import pprint as pp
import json
from spider.parse_sql_one import get_schemas_from_json, Schema
from spider.process_sql import tokenize, get_sql

path = sys.argv[1]
jsons = json.load(open(path))

counts = {
    'all': 0,
    'extra': 0,
    'hard': 0,
    'medium': 0,
    'easy': 0,
}

for (idx, sample) in enumerate(jsons):
    print('[{}] {}'.format(idx, sample['query']))
    counts['all'] += 1
    counts[sample['hardness']] += 1

print(counts)

# %%

# %%
