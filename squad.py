# %%
import json
from pathlib import Path

# %%
def read_squad(path):
    path = Path(path)
    with open(path, 'rb') as f:
        squad_dict = json.load(f)

    contexts = []
    questions = []
    answers = []
    for group in squad_dict['data']:
        for passage in group['paragraphs']:
            context = passage['context']
            for qa in passage['qas']:
                question = qa['question']
                for answer in qa['answers']:
                    contexts.append(context)
                    questions.append(question)
                    answers.append(answer)

    return contexts, questions, answers

# %%
train_contexts, train_questions, train_answers = read_squad('data/squad/train-v2.0.json')
val_contexts, val_questions, val_answers = read_squad('data/squad/dev-v2.0.json')
