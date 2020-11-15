# %%
'''
Count data in the json file for each haedness
'''
from pprint import pprint as pp
import json
from spider.parse_sql_one import get_schemas_from_json, Schema
from spider.process_sql import tokenize, get_sql

# %%
#jsons = json.load(open('data/spider/train_all_cat_aug.json'))
#jsons = json.load(open('data/spider/train_all_cat_aug_easy.json'))
#jsons = json.load(open('data/spider/train_all.json'))
#jsons = json.load(open('data/spider/aug.json'))
jsons = json.load(open('data/spider/tree_trans1.json'))

counts = {
    'all': 0,
    'extra': 0,
    'hard': 0,
    'medium': 0,
    'easy': 0,
}

# %%
for (idx, sample) in enumerate(jsons):
    print('[{}] {}'.format(idx, sample['query']))
    counts['all'] += 1
    counts[sample['hardness']] += 1

# %%
print(counts)

# %%
