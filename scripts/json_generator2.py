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
import json
import requests

generator = Generate()
evaluator = Evaluator()

def validate_question(query: str, parser: SqlParser, question: str) -> bool:
    if ' LIKE ' in query: return True
    if ' like ' in query: return True

    for value in parser.condition_values():
        if value.lower() not in question.lower():
            print('SKIP', value.lower())
            print(query.lower())
            print(question.lower())
            return False

    return True

def convert_question(parser: SqlParser, question: str) -> str:
    if 'desc' in parser.query_parts['order'].lower():
        if 'lowest' in question.lower():
            question = question.replace('lowest', 'highest')
        if 'fewest' in question.lower():
            question = question.replace('fewest', 'most')
        if 'least' in question.lower():
            question = question.replace('least', 'most')

        # TODO: cheapest
    return question

# %%
levels_count = {
    'all': 0,
    'easy': 0,
    'medium': 0,
    'hard': 0,
    'extra': 0,
}
samples: [dict] = []

for i, sql_dict in enumerate(generator.spider_json):
    try:
        db: DB = generator.db_manager.create_db(sql_dict['db_id'])
        parser = SqlParser(sql_dict, db)

        query_alter = QueryAlter(parser, db)
        new_query: str = query_alter.alter()
        sample_dict = {}

        g_sql = get_sql(db.scheme(), new_query)
        hardness: str = evaluator.eval_hardness(g_sql)
        if hardness != 'extra': continue

        data = {'query': new_query}
        res = requests.post('http://127.0.0.1:5000/', json=data)
        question: str = res.json()['res']

        if not question.endswith((',', '?')): continue
        # if not validate_question(new_query, parser, question):
        #     print('SKIP', i)
        #     continue

        question = convert_question(parser, question)

        sample_dict['db_id'] = sql_dict['db_id']
        sample_dict['query'] = new_query

        sample_dict['sql'] = g_sql
        sample_dict['hardness'] = hardness
        sample_dict['question'] = question

        levels_count['all'] += 1
        levels_count[hardness] += 1

        samples.append(sample_dict)
        print('{} {}'.format(levels_count['all'], hardness), end='\t')
        print(new_query)
        print('', end='\t')
        print(question)
        # time.sleep(1)
    except Exception as e:
        #print(e)
        print('', end='')

print(levels_count)

# %%
with open('/Users/aki202/Dev/research/transformer/data/spider/raw/tree_trans5.json', 'w') as f:
    print(json.dumps(samples, indent=4), file=f)

# %%
