# %%
import argparse
import logging
import re
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import nltk
nltk.download('punkt')

import pytorch_lightning as pl

from t5.fine_tuner import T5FineTuner
from t5.default_args import default_args
from common.util import set_seed

from t5_imdb.dataset import ImdbDataset

from transformers import (
    AdamW,
    T5ForConditionalGeneration,
    T5Tokenizer,
    get_linear_schedule_with_warmup
)

# %%
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
args_dict = default_args()

# %%
tokenizer = T5Tokenizer.from_pretrained('t5-base')

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
model.model.save_pretrained('save/t5_base_imdb_sentiment')
model.tokenizer.save_pretrained('save/t5_base_imdb_sentiment')

# %%
