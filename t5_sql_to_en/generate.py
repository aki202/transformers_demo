# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
from spider.process_sql import tokenize
from spider.evaluation import Evaluator
from t5_sql_to_en.dataset import SQLDataset
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer
)
from torch import cuda
from torch.utils.data import DataLoader
import textwrap
import argparse

max_counts = {
    'easy': 1989,
    'medium': 3875,
    'hard': 1467,
    'extra': 1328,
}

# %%
evaluator = Evaluator()

# %%
parser = argparse.ArgumentParser(
    description='evaluate sql_to_en model using t5')
parser.add_argument('-m', '--model', help='model to use',
                    default='t5_sql_to_en__E2')
parser.add_argument('-b', '--batch', help='batch size', type=int, default=64)
if os.environ.get('VSCODE_CLI') == '1':
    params = parser.parse_args(['--model', 't5_sql_to_en__E2'])
else:
    params = parser.parse_args()

print('Model name: {}'.format(params.model))
print('Batch size: {}'.format(params.batch))
print('')

# %%
print('Loading model')
#model = T5ForConditionalGeneration.from_pretrained('t5-base')
model = T5ForConditionalGeneration.from_pretrained('save/' + params.model)
tokenizer = T5Tokenizer.from_pretrained('t5-base')
dataset = SQLDataset(tokenizer, type_path='augmentation_all')

# %%
print('Loading data')
loader = DataLoader(dataset, batch_size=params.batch, shuffle=False)

# %%
counts = {
    'all': 0,
    'extra': 0,
    'hard': 0,
    'medium': 0,
    'easy': 0,
}

# %%
aug_all_json = json.load(open('data/spider/raw/tree_trans13.json'))

# %%
idx = 0
samples = []
for batch in loader:
    # stop if all hardness samples are created
    if levels_count['easy'] >= max_counts['easy'] and \
        levels_count['medium'] >= max_counts['medium'] and \
        levels_count['hard'] >= max_counts['hard'] and \
        levels_count['extra'] >= max_counts['extra']:
        break

    if cuda.is_available():
        model.to('cuda')
        source_ids = batch['source_ids'].cuda()
        source_mask = batch['source_mask'].cuda()
    else:
        source_ids = batch['source_ids']
        source_mask = batch['source_mask']

    outs = model.generate(input_ids=source_ids, attention_mask=source_mask)

    dec = [tokenizer.decode(ids) for ids in outs]

    texts = [tokenizer.decode(ids) for ids in batch['source_ids']]

    for i in range(len(texts)):
        sample_id = batch['id'][i].item()
        sql_g = dataset.sql_graphs[sample_id]
        hardness = evaluator.eval_hardness(sql_g)

        raw_sql = texts[i].replace('translate SQL to English: ', '')
        sql_disp = '\n'.join(textwrap.wrap(raw_sql, width=100))

        print(dec[i])

        cataloged = 'NG'
        if dec[i].endswith(('.', '?')):
            if counts[hardness] > max_counts[hardness]-1:
                print('Skip: Reached max count ({}, {})'.format(hardness, max_counts[hardness]))

            aug_all_json[idx]['question'] = dec[i]
            samples.append(aug_all_json[idx])
            counts['all'] += 1
            counts[hardness] += 1
            cataloged = 'OK'

        print('[{}] SQL: {}'.format(idx, sql_disp))
        print('hardness: {}'.format(hardness))
        print("Predicted: %s" % dec[i])
        print('Cataloged: {}'.format(cataloged))
        print("=====================================================================\n")
        idx += 1

# %%
print("Total count: {}".format(counts['all']))

# %%
with open('data/spider/tree_trann13.json', 'w') as f:
    print(json.dumps(samples, indent=4), file=f)

# %%
