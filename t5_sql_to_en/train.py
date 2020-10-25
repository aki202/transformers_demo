# %%
import argparse
import nltk
nltk.download('punkt')
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pytorch_lightning as pl
from transformers import T5Tokenizer

from t5.fine_tuner import T5FineTuner
from t5.default_args import default_args
from t5_sql_to_en.dataset import SQLDataset
from common.util import set_seed

# %%
set_seed(42)
args_dict = default_args()

# %%
tokenizer = T5Tokenizer.from_pretrained(args_dict['tokenizer_name_or_path'])

# %%
def get_dataset(tokenizer, type_path, args):
    return SQLDataset(tokenizer=tokenizer, type_path=type_path)

# %%
args_dict.update({
    'output_dir': 'results/t5_sql_to_en',
    'train_batch_size': 1,
    'eval_batch_size': 1,
    'num_train_epochs': 2,
    'get_dataset': get_dataset,
})
args = argparse.Namespace(**args_dict)

train_params = dict(
    accumulate_grad_batches=args.gradient_accumulation_steps,
    gpus=args.n_gpu,
    max_epochs=args.num_train_epochs,
    early_stop_callback=False,
    precision= 16 if args.fp_16 else 32,
    amp_level=args.opt_level,
    gradient_clip_val=args.max_grad_norm
)

# %%
model = T5FineTuner(args)

# %%
trainer = pl.Trainer(**train_params)

# %%
trainer.fit(model)

# %%
# save the model this way so next time you can load it using T5ForConditionalGeneration.from_pretrained
model.model.save_pretrained('save/t5_sql_to_en')
model.tokenizer.save_pretrained('save/t5_sql_to_en')

# %%
