# %%
import glob
import os
import json
import re
from torch.utils.data import Dataset

# %%
class SQLDataset(Dataset):
    def __init__(self, tokenizer, type_path = 'train'):
        self.tokenizer = tokenizer
        self.type_path = type_path
        self.inputs = []
        self.targets = []

        self._build()

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, index):
        source_ids = self.inputs[index]["input_ids"].squeeze()
        target_ids = self.targets[index]["input_ids"].squeeze()

        source_mask = self.inputs[index]["attention_mask"].squeeze() # might need to squeeze
        target_mask = self.targets[index]["attention_mask"].squeeze() # might need to squeeze

        return {
            "source_ids": source_ids,
            "source_mask": source_mask,
            "target_ids": target_ids,
            "target_mask": target_mask
        }

    def _build_from_file(self, filename):
        spider_json = json.load(open('./data/spider/{}.json'.format(filename)))

        for datum in spider_json:
            source = 'translate SQL to English: {} </s>'.format(datum['query'])
            target = '{} </s>'.format(datum['question'])

            # tokenize inputs
            tokenized_inputs = self.tokenizer.batch_encode_plus(
                [source], max_length=250, padding='max_length', return_tensors="pt",
                truncation=True
            )
            # tokenize targets
            tokenized_targets = self.tokenizer.batch_encode_plus(
                [target], max_length=50, padding='max_length', return_tensors="pt",
                truncation=True
            )
            #print('x:{},\ty:{},\t{}\t{}'.format(x, y, source, target))

            self.inputs.append(tokenized_inputs)
            self.targets.append(tokenized_targets)

    def _build(self):
        if self.type_path == 'train':
            self._build_from_file('train_spider')
            self._build_from_file('train_others')
        elif self.type_path == 'val':
            self._build_from_file('dev')
        else: raise 'Invalid type_path ({})'.format(self.type_path)

# %%
if __name__ == '__main__':
    from transformers import T5Tokenizer
    tokenizer = T5Tokenizer.from_pretrained('t5-base')
# %%
    dataset = SQLDataset(tokenizer, type_path='train')
# %%
    print('len={}'.format(len(dataset)))
    print(dataset[0]['source_ids'].shape)
    print(dataset[1]['source_ids'].shape)
    print(dataset[2]['source_ids'].shape)
    data = dataset[10]
    print(data)
    for _id in data['source_ids']:
        id = _id.item()
        token = tokenizer.decode(id)
        print('{}({}), '.format(token, id), end='')
    print('')
    print("'{}'".format(tokenizer.decode(data['source_ids'])))
    print("'{}'".format(tokenizer.decode(data['target_ids'])))

# %%
