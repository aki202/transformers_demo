# %%
name = 'tree_trans7_extra'
path = 'data/spider/{}.json'.format(name)

from pprint import pprint as pp
import json
from generator.generate import Generate
from generator.sql_parser import SqlParser
from generator.db import DB

generator = Generate()
jsons = json.load(open(path))

def validate_question(sample) -> bool:
    try:
        db: DB = generator.db_manager.create_db(sample['db_id'])
        parser = SqlParser(sample, db)
        query: str = sample['query']
        question: str = sample['question']
    except Exception as e:
        return False

    if ' LIKE ' in query: return True
    if ' like ' in query: return True

    for value in parser.condition_values():
        if len(value) < 2: continue
        if value.lower() not in question.lower():
            print('SKIP', value.lower())
            print(query.lower())
            print(question.lower())
            return False

    return True

counts = {
    True: 0,
    False: 0,
}

new_samples = []
for (idx, sample) in enumerate(jsons):
    #print('{}: {}'.format(idx, sample['query']))
    val = validate_question(sample)
    print('{} {}'.format(idx, val))
    counts[val] += 1
    if val: new_samples.append(sample)

print(counts)
outpath = 'data/spider/{}_vw.json'.format(name)
with open('/Users/aki202/Dev/research/transformer/{}'.format(outpath), 'w') as f:
    print(json.dumps(new_samples, indent=4), file=f)

# %%
