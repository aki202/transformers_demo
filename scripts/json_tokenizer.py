# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
from spider.process_sql import tokenize, get_sql
from spider.parse_sql_one import get_schemas_from_json, Schema
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('json_name', type=str)
args = parser.parse_args()

# %%
schemas, db_names, tables = get_schemas_from_json('data/spider/tables.json')

# %%
jsons = json.load(open('data/spider/raw/{}'.format(args.json_name)))

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
    try:
        schema = schemas[sample['db_id']]
        table = tables[sample['db_id']]
        schema = Schema(schema, table)
        sql = get_sql(schema, sample['query'])

        sample['query_toks'] = tokenize(sample['query'])
        sample['query_toks_no_value'] = tokenize(sample['query'])
        sample['question_toks'] = tokenize(sample['question'])
        sample['sql'] = sql
        counts['all'] += 1
        counts[sample['hardness']] += 1
        new_samples.append(sample)
    except Exception as e:
        print(e)

# %%
with open('data/spider/{}'.format(args.json_name), 'w') as f:
    print(json.dumps(new_samples, indent=4), file=f)

# %%
print(counts)

# %%
