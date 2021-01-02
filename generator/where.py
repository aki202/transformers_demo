# %%
import re
from generator.column import Column
from generator.db import DB
from generator.alias_manager import AliasManager

#WHERE_OPS = ('not', 'between', '=', '>', '<', '>=', '<=', '!=', 'in', 'like', 'is', 'exists')
OPS = ('=', '>', '<', '>=', '<=', '!=', 'in', 'not in', 'like', 'between')

pattern = re.compile(r'''
    \s*
    (?P<col>[^\s]+)
    \s+
    (?P<op>=|>|<|>=|<=|!=|in|not\ in|like|between)
    \s+
    (?P<val>.+)
    \s*
''', re.IGNORECASE + re.VERBOSE)

class Where:
    def __init__(self, column: Column, op: int, value: str):
        self.column: Column = column
        self.op: int = op
        self.value: str = value

    def __str__(self):
        return '{}, op:{}, val:{}'.format(self.column, OPS[self.op], self.value)

def parse_to_where(raw: str, db: DB, alias_manager: AliasManager) -> Where:
    match: re.Match = pattern.match(raw)
    hits: {str: str} = match.groupdict()
    col_raw: str = hits['col']
    op_raw: str = hits['op']
    val_raw: str = hits['val']

    parts = col_raw.split('.')
    if len(parts) > 1:
        col_name = parts[1]
        alias = parts[0]
    else:
        col_name = parts[0]
        if col_name == '*':
            alias = -1
        else:
            alias = None

    # find table alias
    table_id = db.table_id_by_alias(alias, alias_manager)
    column = db.column(col_name, table_id)

    # find op
    op = OPS.index(op_raw.lower())

    return Where(column, op, val_raw)

# %%
if __name__ == '__main__':
    db = DB({
        'column_names_original': [
            [-1, '*'],
            [0, 'id'],
            [1, 'name'],
            [1, 'age'],
        ],
        'table_names_original': ['Invoices', 'Customers']
    })
    am = AliasManager()
    am.add(None, 0)
    am.add('T1', 0)
    am.add('T2', 1)
    print(parse_to_where('T2.age <= 40', db, am))
    print(parse_to_where('T1.id between 10 and 20', db, am))
    print(parse_to_where('T1.id = 10', db, am))
    print(parse_to_where('T1.id != 10', db, am))
    print(parse_to_where('T1.id > 10', db, am))
    print(parse_to_where('T1.id < 10', db, am))
    print(parse_to_where('T1.id >= 10', db, am))
    print(parse_to_where('T1.id <= 10', db, am))
    print(parse_to_where('T1.id IN (SELECT id FROM users)', db, am))
    print(parse_to_where('T1.id NOT IN (SELECT id FROM users)', db, am))

# %%

# %%
