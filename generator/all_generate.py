# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
from pprint import pprint as pp

# %%
train_spider_json = json.load(open('data/spider/train_spider.json'))
train_others_json = json.load(open('data/spider/train_others.json'))

# %%
tables_counts = {
    0: 0,
    1: 0,
    2: 0,
    3: 0,
    4: 0,
}

for i, js in enumerate(train_spider_json):
    units = len(js['sql']['from']['table_units'])
    tables_counts[units] += 1
    if units > 3:
        print(i)
        print(js)

for js in train_others_json:
    units = len(js['sql']['from']['table_units'])
    tables_counts[units] += 1

pp(tables_counts)

# %%
