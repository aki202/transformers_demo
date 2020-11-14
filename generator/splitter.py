# %%
from pprint import pprint as pp

KW = ['select', 'from', 'join', 'where', 'group', 'having', 'order', 'limit']

def split(query: str):
    nest_count: int = 0
    all_toks: {str: str} = {
        'select': [],
        'from': [],
        'join': [],
        'where': [],
        'group': [],
        'having': [],
        'order': [],
        'limit': [],
    }
    #query = query.replace('(', ' ( ')
    #query = query.replace(')', ' ) ')
    query = query.replace(';', '')
    toks: [str] = query.split(' ')
    current_mode: str = None
    for tok in toks:
        if '(' in tok: nest_count += 1
        if ')' in tok: nest_count -= 1
        if tok.lower() in KW and nest_count == 0: current_mode = tok.lower()
        if len(tok) > 0: all_toks[current_mode].append(tok)

    for k in all_toks:
        all_toks[k] = ' '.join(all_toks[k])

    return all_toks

# %%
if __name__ == '__main__':
    #query = 'SELECT T1.Continent ,  count(*) FROM CONTINENTS AS T1 JOIN COUNTRIES AS T2 ON T1.ContId  =  T2.continent JOIN car_makers AS T3 ON T2.CountryId  =  T3.Country GROUP BY T1.Continent;'
    #query = 'SELECT avg(grade) FROM Highschooler WHERE id IN (SELECT T1.student_id FROM Friend AS T1 JOIN Highschooler AS T2 ON T1.student_id  =  T2.id)'
    #query = 'SELECT T1.Model FROM CAR_NAMES AS T1 JOIN CARS_DATA AS T2 ON T1.MakeId  =  T2.Id ORDER BY T2.horsepower ASC LIMIT 1;'
    query = 'SELECT DISTINCT product_name FROM products ORDER BY product_name'
    components = split(query)
    pp(components)

# %%
