# %%
import re

def convert_pair(question: str, query: str) -> list:
    _question = question.lower()
    _query = query.lower()
    _question = replace_text(_question)
    _query = replace_text(_query)
    _question = replace_number(_question)
    _query = replace_number(_query)
    return [_question, _query]

def replace_text(target: str) -> str:
    matches = re.findall('[\'"].+?[\'"]', target)
    for (i, match) in enumerate(matches):
        target = target.replace(match, 'VALUE_{}'.format(i))
    return target

def replace_number(target: str) -> str:
    matches = re.findall(' \d+ ', target)
    for (i, match) in enumerate(matches):
        target = target.replace(match, ' NUMBER_{} '.format(i))
    return target

# %%
if __name__ == '__main__':
    target = 'where name = "test" and like = "apple"'
    assert replace_text(target) == 'where name = VALUE_0 and like = VALUE_1'
    target = "where name = 'test' and like = 'apple'"
    assert replace_text(target) == 'where name = VALUE_0 and like = VALUE_1'

    target = "T0.id > 1 and T1.age < 10 "
    assert replace_number(target) == 'T0.id > NUMBER_0 and T1.age < NUMBER_1 ', replace_number(target)

# %%
