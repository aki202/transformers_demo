# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
from spider.process_sql import tokenize, get_sql
from spider.parse_sql_one import get_schemas_from_json, Schema

# %%
#jsons = json.load(open('data/spider/train_all_cat_aug.json'))
jsons = json.load(open('data/spider/train_all_cat_aug_easy.json'))
#jsons = json.load(open('data/spider/train_all.json'))
#jsons = json.load(open('data/spider/aug.json'))

counts = {
    'all': 0
}

# %%
for (idx, sample) in enumerate(jsons):
    print('[{}] {}'.format(idx, sample['query']))
    counts['all'] += 1

# %%
print(counts)

# %%
