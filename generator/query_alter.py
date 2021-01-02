# %%
from generator.sql_parser import SqlParser
from generator.select_column import SelectColumn
from generator.db import DB
import random

class QueryAlter:
    def __init__(self, parser: SqlParser, db: DB):
        self.parser: SqlParser = parser
        self.db = db

    def find_change_column(self) -> SelectColumn:
        for select_column in random.sample(self.parser.select_columns, len(self.parser.select_columns)):
            if select_column.agg != None: continue
            return select_column

    def alter(self) -> SqlParser:
        change_column = self.find_change_column()
        if change_column == None: raise Exception('Not find select column to change')

        used_column_ids: [int] = [s.column.column_idx for s in self.parser.select_columns]

        new_select_column: SelectColumn
        for column in random.sample(self.db.columns, len(self.db.columns)):
            if change_column.column.table_idx != column.table_idx: continue
            if column.column_idx in used_column_ids: continue
            new_select_column = SelectColumn(
                column,
                agg=change_column.agg,
                distinct=change_column.distinct
            )

        new_select_columns: [SelectColumn] = [
            new_select_column if s == change_column else s for s in self.parser.select_columns
        ]
        self.parser.select_columns = new_select_columns
        return self.parser.to_query()

if __name__ == '__main__':
    from generator.generate import Generate
    from pprint import pprint as pp

    generator = Generate()
    idx: int = 0
    sql_dict = generator.spider_json[idx]
    db = generator.db_manager.create_db(sql_dict['db_id'])
    parser = SqlParser(sql_dict, db)

    print('ORG: {}'.format(sql_dict['query']))
    query_alter = QueryAlter(parser, db)
    new_query: str = query_alter.alter()
    print('NEW: {}'.format(new_query))

    # conditions
    # 1. not using group
    # 2. a column that has format as {table}.{column}
    # 4. a column not using agg operation
    # 5.

    # if using group, change grouped column

# %%
