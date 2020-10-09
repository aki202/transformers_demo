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
from nltk import bleu_score, word_tokenize

# %%
parser = argparse.ArgumentParser(description='evaluate sql_to_en model using t5')
parser.add_argument('-m', '--model', help='model to use', default='t5_sql_to_en__E1')
params = parser.parse_args()

print('Loading ' + params.model)

# %%
#model = T5ForConditionalGeneration.from_pretrained('save/t5_sql_to_en__epoch3')
model = T5ForConditionalGeneration.from_pretrained('save/' + params.model)
#tokenizer = T5Tokenizer.from_pretrained('save/t5_sql_to_en__epoch3')
tokenizer = T5Tokenizer.from_pretrained('t5-base')
dataset = SQLDataset(tokenizer, type_path='val')

# %%
print('Loading data')
loader = DataLoader(dataset, batch_size=64, shuffle=True)

# %%
all_blue4 = 0

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
    targets = [tokenizer.decode(ids) for ids in batch['target_ids']]

    for i in range(len(texts)):
        lines = textwrap.wrap(texts[i], width=100)
        sql = '\n'.join(lines).replace('translate SQL to English: ', '')

        hy = word_tokenize(dec[i])
        re = word_tokenize(targets[i])
        blue4 = bleu_score.sentence_bleu([re], hy)
        all_blue4 += blue4

        print('SQL: {}'.format(sql))
        print("\nActual: %s" % targets[i])
        print("Predicted: %s" % dec[i])
        print("Blue-4: {}".format(blue4))
        print("=====================================================================\n")

print("Total count: {}".format(len(dataset)))
print("Total Blue-4: {}".format(all_blue4 / len(dataset)))
