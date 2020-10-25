# %%
import re

def convert_pair(question: str, query: str) -> list:
    _question = question.lower()
    _query = query.lower()

    #question_matches = matches_in_text(question)
    #query_matches = matches_in_text(query)
    #if len(question_matches) == len(query_matches):
    #    _question = replace_text(_question)
    #    _query = replace_text(_query)
    #_question = replace_number(_question)
    #_query = replace_number(_query)
    return [_question, _query]

def matches_in_text(target: str) -> list:
    return re.findall('[\'"].+?[\'"]', target)

def replace_text(target: str) -> str:
    matches = matches_in_text(target)
    for (i, match) in enumerate(matches):
        target = target.replace(match, 'value_{}'.format(i))
    return target

def replace_number(target: str) -> str:
    matches = re.findall(' \d+ ', target)
    for (i, match) in enumerate(matches):
        target = target.replace(match, ' number_{} '.format(i))
    return target

# %%
if __name__ == '__main__':
    target = 'where name = "test" and like = "apple"'
    assert replace_text(target) == 'where name = value_0 and like = value_1'
    target = "where name = 'test' and like = 'apple'"
    assert replace_text(target) == 'where name = value_0 and like = value_1'

    target = "T0.id > 1 and T1.age < 10 "
    assert replace_number(target) == 'T0.id > number_0 and T1.age < number_1 ', replace_number(target)

# %%
