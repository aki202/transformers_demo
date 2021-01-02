# %%
'''
Generate json file with "question" as null
'''
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

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

max_counts = {
    'easy': 1989*5,
    'medium': 3875*5,
    'hard': 1467*5,
    'extra': 1328*5,
}

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

def add_to_samples():
    for sql_dict in generator.spider_json:
        try:
            db: DB = generator.db_manager.create_db(sql_dict['db_id'])
            parser = SqlParser(sql_dict, db)
            #if len(parser.query_parts['group']) > 0: continue

            query_alter = QueryAlter(parser, db)
            new_query: str = query_alter.alter()
            sample_dict = {}

            tokens = tokenizer.tokenize(new_query)

            g_sql = get_sql(db.scheme(), new_query)
            hardness: str = evaluator.eval_hardness(g_sql)

            # skip if the number of the level's samples reached max count
            if levels_count[hardness] > max_counts[hardness]-1: continue

            sample_dict['db_id'] = sql_dict['db_id']
            sample_dict['query'] = new_query

            sample_dict['sql'] = g_sql
            sample_dict['hardness'] = hardness
            sample_dict['question'] = ''
            sample_dict['original_question'] = sql_dict['question']

            levels_count['all'] += 1
            levels_count[hardness] += 1

            samples.append(sample_dict)
            print('{} {}'.format(levels_count['all'], hardness), end='\t')
            print(new_query)
            # time.sleep(1)
        except Exception as e:
            #print(e)
            print('', end='')

c = 0
while True:
    print('loop: {}'.format(c))
    c += 1
    add_to_samples()
    if levels_count['easy'] < max_counts['easy']: continue
    if levels_count['medium'] < max_counts['medium']: continue
    if levels_count['hard'] < max_counts['hard']: continue
    if levels_count['extra'] < max_counts['extra']: continue
    break

print(levels_count)
with open('/Users/aki202/Dev/research/transformer/data/spider/raw/tree_trans15.json', 'w') as f:
    print(json.dumps(samples, indent=4), file=f)

# %%
