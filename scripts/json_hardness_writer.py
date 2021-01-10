# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
from spider.process_sql import tokenize, get_sql
from spider.parse_sql_one import get_schemas_from_json, Schema
from spider.evaluation import Evaluator

src = sys.argv[1]
dst = sys.argv[2]
evaluator = Evaluator()

counts = {
    'all': 0,
    'extra': 0,
    'hard': 0,
    'medium': 0,
    'easy': 0,
}

# %%
jsons = json.load(open('data/spider/{}.json'.format(src)))

# %%
new_samples = []
for (idx, sample) in enumerate(jsons):
    print('[{}] {}'.format(idx, sample['query']))
    if 'hardness' not in sample:
        hardness: str = evaluator.eval_hardness(sample['sql'])
        sample['hardness'] = hardness
    counts['all'] += 1
    counts[sample['hardness']] += 1
    new_samples.append(sample)

print(counts)

# %%
with open('data/spider/{}.json'.format(dst), 'w') as f:
    print(json.dumps(new_samples, indent=4), file=f)

