# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
from spider.process_sql import tokenize

jsons = json.load(open('data/spider/aug_all_with_q.json'))

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
    try:
        sample['query_toks'] = tokenize(sample['query'])
        sample['query_toks_no_value'] = tokenize(sample['query'])
        sample['question_toks'] = tokenize(sample['question'])
        counts['all'] += 1
        counts[sample['hardness']] += 1
    except Exception as e:
        print(e)

# %%
with open('data/spider/aug.json', 'w') as f:
    print(json.dumps(jsons, indent=4), file=f)

# %%
print(counts)
