# %%
import torch

# %%
def default_args():
    return dict(
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
