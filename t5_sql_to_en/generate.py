# %%
import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import textwrap
from torch.utils.data import DataLoader
from torch import cuda
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer
)

from t5_sql_to_en.dataset import SQLDataset
from spider.evaluation import Evaluator

# %%
evaluator = Evaluator()

# %%
parser = argparse.ArgumentParser(description='evaluate sql_to_en model using t5')
parser.add_argument('-m', '--model', help='model to use', default='t5_sql_to_en')
parser.add_argument('-b', '--batch', help='batch size', type=int, default=64)
#params = parser.parse_args(args=[])
params = parser.parse_args()

print('Model name: {}'.format(params.model))
print('Batch size: {}'.format(params.batch))
print('')

# %%
print('Loading model')
model = T5ForConditionalGeneration.from_pretrained('t5-base')
#model = T5ForConditionalGeneration.from_pretrained('save/' + params.model)
tokenizer = T5Tokenizer.from_pretrained('t5-base')
dataset = SQLDataset(tokenizer, type_path='augmentation_all')

# %%
print('Loading data')
loader = DataLoader(dataset, batch_size=params.batch)

# %%
counts = {
    'all': 0,
    'extra': 0,
    'hard': 0,
    'medium': 0,
    'easy': 0,
}

# %%
for batch in loader:
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

        counts['all'] += 1
        counts[hardness] += 1

        print('SQL: {}'.format(sql_disp))
        print('hardness: {}'.format(hardness))
        print("Predicted: %s" % dec[i])
        print("=====================================================================\n")

# %%
print("Total count: {}".format(counts['all']))

# %%
