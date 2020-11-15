# %%
'''
Generate json file with "question" as null
'''
from generator.query_alter import QueryAlter
from generator.generate import Generate
from generator.sql_parser import SqlParser
from generator.db import DB
from pprint import pprint as pp
from spider.process_sql import get_sql
from spider.evaluation import Evaluator
from transformers import T5Tokenizer
import json
tokenizer = T5Tokenizer.from_pretrained('t5-base')

generator = Generate()
evaluator = Evaluator()

levels_count = {
    'all': 0,
    'easy': 0,
    'medium': 0,
    'hard': 0,
    'extra': 0,
}
samples: [dict] = []

for sql_dict in generator.spider_json:
    try:
        db: DB = generator.db_manager.create_db(sql_dict['db_id'])
        parser = SqlParser(sql_dict, db)
        if len(parser.query_parts['group']) > 0: continue

        query_alter = QueryAlter(parser, db)
        new_query: str = query_alter.alter()
        sample_dict = {}

        tokens = tokenizer.tokenize(new_query)
        if len(tokens) > 100: raise Exception('token are too much')

        g_sql = get_sql(db.scheme(), new_query)
        hardness: str = evaluator.eval_hardness(g_sql)

        sample_dict['db_id'] = sql_dict['db_id']
        sample_dict['query'] = new_query

        sample_dict['sql'] = g_sql
        sample_dict['hardness'] = hardness
        sample_dict['question'] = ''

        levels_count['all'] += 1
        levels_count[hardness] += 1

        samples.append(sample_dict)
        print('{} {}'.format(levels_count['all'], hardness), end='\t')
        print(new_query)
        # time.sleep(1)
    except Exception as e:
        #print(e)
        print('', end='')

print(levels_count)
with open('/Users/aki202/Dev/research/transformer/data/spider/raw/tree_trans1.json', 'w') as f:
    print(json.dumps(samples, indent=4), file=f)

# %%
