# %%
import argparse
import glob
import os
import json
import time
import logging
import random
import re
from itertools import chain
from string import punctuation

import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
import pytorch_lightning as pl

from t5.fine_tuner import T5FineTuner

from transformers import (
    AdamW,
    T5ForConditionalGeneration,
    T5Tokenizer,
    get_linear_schedule_with_warmup
)

# %%
def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(42)

# %%
logger = logging.getLogger(__name__)

class LoggingCallback(pl.Callback):
    def on_validation_end(self, trainer, pl_module):
        logger.info("***** Validation results *****")
        if pl_module.is_logger():
            metrics = trainer.callback_metrics
            # Log results
            for key in sorted(metrics):
                if key not in ["log", "progress_bar"]:
                    logger.info("{} = {}\n".format(key, str(metrics[key])))

    def on_test_end(self, trainer, pl_module):
        logger.info("***** Test results *****")

        if pl_module.is_logger():
            metrics = trainer.callback_metrics

        # Log and save results to file
        output_test_results_file = os.path.join(pl_module.hparams.output_dir, "test_results.txt")
        with open(output_test_results_file, "w") as writer:
            for key in sorted(metrics):
                if key not in ["log", "progress_bar"]:
                    logger.info("{} = {}\n".format(key, str(metrics[key])))
                    writer.write("{} = {}\n".format(key, str(metrics[key])))

# %%
args_dict = dict(
    data_dir="", # path for data files
    output_dir="", # path to save the checkpoints
    model_name_or_path='t5-base',
    tokenizer_name_or_path='t5-base',
    max_seq_length=512,
    learning_rate=3e-4,
    weight_decay=0.0,
    adam_epsilon=1e-8,
    warmup_steps=0,
    train_batch_size=1,
    eval_batch_size=1,
    num_train_epochs=1,
    gradient_accumulation_steps=1,
    n_gpu= 1 if torch.cuda.is_available() else 0,
    early_stop_callback=False,
    fp_16=False, # if you want to enable 16-bit training then install apex and set this to true
    opt_level='O1', # you can find out more on optimisation levels here https://nvidia.github.io/apex/amp.html#opt-levels-and-properties
    max_grad_norm=1.0, # if you enable 16-bit training then set this to a sensible value, 0.5 is a good default
    seed=42,
)

# %%
tokenizer = T5Tokenizer.from_pretrained('t5-base')

# %%
ids_neg = tokenizer.encode('negative </s>')
ids_pos = tokenizer.encode('positive </s>')
len(ids_neg), len(ids_pos)

# %%
class ImdbDataset(Dataset):
    def __init__(self, tokenizer, data_dir, type_path,  max_len=512):
        self.pos_file_path = os.path.join(data_dir, type_path, 'pos')
        self.neg_file_path = os.path.join(data_dir, type_path, 'neg')

        self.pos_files = glob.glob("%s/*.txt" % self.pos_file_path)
        self.neg_files = glob.glob("%s/*.txt" % self.neg_file_path)

        self.max_len = max_len
        self.tokenizer = tokenizer
        self.inputs = []
        self.targets = []

        self._build()

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, index):
        source_ids = self.inputs[index]["input_ids"].squeeze()
        target_ids = self.targets[index]["input_ids"].squeeze()

        src_mask    = self.inputs[index]["attention_mask"].squeeze()  # might need to squeeze
        target_mask = self.targets[index]["attention_mask"].squeeze()  # might need to squeeze

        return {"source_ids": source_ids, "source_mask": src_mask, "target_ids": target_ids, "target_mask": target_mask}

    def _build(self):
        self._buil_examples_from_files(self.pos_files, 'positive')
        self._buil_examples_from_files(self.neg_files, 'negative')

    def _buil_examples_from_files(self, files, sentiment):
        REPLACE_NO_SPACE = re.compile("[.;:!\'?,\"()\[\]]")
        REPLACE_WITH_SPACE = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)")

        for path in files:
            with open(path, 'r') as f:
                text = f.read()

            line = text.strip()
            line = REPLACE_NO_SPACE.sub("", line)
            line = REPLACE_WITH_SPACE.sub("", line)
            line = line + ' </s>'

            target = sentiment + " </s>"

            # tokenize inputs
            tokenized_inputs = self.tokenizer.batch_encode_plus(
                [line], max_length=self.max_len, pad_to_max_length=True,
                return_tensors="pt", truncation=True
            )
            # tokenize targets
            tokenized_targets = self.tokenizer.batch_encode_plus(
                [target], max_length=2, pad_to_max_length=True,
                return_tensors="pt", truncation=True
            )

            self.inputs.append(tokenized_inputs)
            self.targets.append(tokenized_targets)

# %%
'''
dataset = ImdbDataset(tokenizer, 'data/aclImdb', 'val', max_len=512)
print(len(dataset))

data = dataset[28]
print(tokenizer.decode(data['source_ids']))
print(tokenizer.decode(data['target_ids']))
'''

# %%
def get_dataset(tokenizer, type_path, args):
    return ImdbDataset(tokenizer=tokenizer, data_dir=args.data_dir,
        type_path=type_path,  max_len=args.max_seq_length)

# %%
args_dict.update({
    'data_dir': 'data/aclImdb',
    'output_dir': 'results/t5_imdb_sentiment',
    'num_train_epochs': 1,
    'get_dataset': get_dataset,
})
args = argparse.Namespace(**args_dict)

checkpoint_callback = pl.callbacks.ModelCheckpoint(
    filepath=args.output_dir,
    prefix="checkpoint",
    monitor="val_loss",
    mode="min",
    save_top_k=5
)

train_params = dict(
    accumulate_grad_batches=args.gradient_accumulation_steps,
    gpus=args.n_gpu,
    max_epochs=args.num_train_epochs,
    early_stop_callback=False,
    precision= 16 if args.fp_16 else 32,
    amp_level=args.opt_level,
    gradient_clip_val=args.max_grad_norm,
    checkpoint_callback=checkpoint_callback,
    callbacks=[LoggingCallback()],
)

# %%
model = T5FineTuner(args)

# %%
trainer = pl.Trainer(**train_params)

# %%
trainer.fit(model)

# %%
# save the model this way so next time you can load it using T5ForConditionalGeneration.from_pretrained
model.model.save_pretrained('t5_base_imdb_sentiment')
model.tokenizer.save_pretrained('t5_base_imdb_sentiment')
