# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
from spider.process_sql import tokenize, get_sql
from spider.parse_sql_one import get_schemas_from_json, Schema
from spider.evaluation import Evaluator


# %%
schemas, db_names, tables = get_schemas_from_json('data/spider/tables.json')
evaluator = Evaluator()

# %%
jsons = json.load(open('data/spider/train_others300.json'))

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
        hardness = evaluator.eval_hardness(sql)

        sample['query_toks'] = tokenize(sample['query'])
        sample['query_toks_no_value'] = tokenize(sample['query'])
        sample['question_toks'] = tokenize(sample['question'])
        sample['hardness'] = hardness
        sample['sql'] = sql
        counts['all'] += 1
        counts[hardness] += 1
        new_samples.append(sample)
    except Exception as e:
        print(e)

# %%
with open('data/spider/train_others300edited.json', 'w') as f:
    print(json.dumps(new_samples, indent=4), file=f)

# %%
print(counts)

# %%
