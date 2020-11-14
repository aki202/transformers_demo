# %%
from generator.column import Column
from generator.table import Table
from generator.db import DB
from generator.alias_manager import AliasManager
import re

AGG = ('max', 'min', 'count', 'sum', 'avg')

class SelectColumn:
    def __init__(self, column: Column, agg: int, distinct: bool):
        self.column: Column = column
        self.agg: int or None = agg
        self.distinct: bool = distinct

    def __str__(self) -> str:
        return '{}, distinct: {}, agg: {}'.format(
            self.column,
            self.distinct,
            self.agg
        )

    def to_query(self, alias_manager: AliasManager) -> str:
        query: str = ''
        if len(alias_manager) < 3: # only none
            query = self.column.name
        else:
            alias: str = alias_manager.alias(self.column.table_idx)
            if alias:
                query = '{}.{}'.format(alias, self.column.name)
            else:
                query = self.column.name

        # it distinct is used
        if self.distinct:
            query = 'DISTINCT {}'.format(query)

        # if agg is used
        if self.agg != None:
            query = '{}({})'.format(AGG[self.agg], query)

        return query

def parse_to_select_column(raw: str, db: DB, alias_manager: AliasManager) -> SelectColumn:
    '''
    e.g.
    - max(DISTINCT T1.name)
    - DISTINCT T1.name
    '''
    raw = raw.strip()
    agg_id: int = None

    # distinct(*) -> distinct *
    raw = re.sub(r'distinct\((.+?)\)', r'distinct \1', raw)

    # find agg function
    agg_matches: re.Match = re.search(r'([a-z]+)\s*\((.+?)\)', raw, flags=re.IGNORECASE)
    if agg_matches:
        raw_matched: str = agg_matches[1].strip()
        agg_id = AGG.index(raw_matched.lower())
        raw = agg_matches[2].strip()

    # find distinct function
    distinct_matches: re.Match = re.search(r'^distinct *(.+?) *$', raw, flags=re.IGNORECASE)
    using_distinct: bool = False
    if distinct_matches:
        using_distinct = True
        raw = distinct_matches[1].strip()

    parts = raw.split('.')
    if len(parts) > 1:
        col_name = parts[1]
        alias = parts[0]
    else:
        col_name = parts[0]
        if col_name == '*':
            alias = -1
        else:
            alias = None

    try:
        # find table alias
        table_id = db.table_id_by_alias(alias, alias_manager)
        column = db.column(col_name, table_id, alias_manager)
    except Exception as e:
        print('not found col_name {}(table_idx={}, alias={})'.format(col_name, table_id, alias))
        for col in db.columns: print(col)
        raise e

    # create SelectColumn
    return SelectColumn(column, agg_id, using_distinct)

# %%
if __name__ == '__main__':
    import json
    from generator.db_manager import DBManager
    from pprint import pprint as pp

    train_spider_json = json.load(open('data/spider/train_spider.json'))
    sql_dict = train_spider_json[13]
    db_manager = DBManager('data/spider/tables.json')
    db = db_manager.create_db(sql_dict['db_id'])
    #pp(sql_dict)
    #pp(db.db_dict)
    # table_names': ['department', 'head', 'management'],
    am1 = AliasManager()
    am1.add(None, 0)
    am1.add('T1', 0)
    am1.add('T2', 1)
    select_column1 = parse_to_select_column('sum(DISTINCT T2.name)', db, am1)
    print('select_column1', select_column1)
    print('query', select_column1.to_query(am1))
    select_column2 = parse_to_select_column('distinct(name)', db, am1)
    print('select_column2', select_column2)
    print('query', select_column2.to_query(am1))

# %%

# %%
