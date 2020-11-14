# %%
from generator.table import Table
from generator.column import Column
from generator.alias_manager import AliasManager
from pprint import pprint as pp
from spider.process_sql import get_schema, Schema

SQL_PATH = '/Users/aki202/Dev/python/jspider/database/'

class DB:
    def __init__(self, db_dict: dict) -> None:
        self.db_dict = db_dict
        self.tables: {int: Table} = {}
        self.columns: [Column] = []

        # create tables
        for (idx, name) in enumerate(self.db_dict['table_names_original']):
            self.tables[idx] = Table(name, idx)

        # create columns
        for (col_idx, col_arr) in enumerate(self.db_dict['column_names_original']):
            table_idx: int = int(col_arr[0])
            name: str = col_arr[1]
            self.columns.append(Column(name, col_idx, table_idx))

    def table_name(self, idx: int) -> str:
        return self.tables[idx].name

    def table_id_by_alias(self, alias: str or int, alias_manager: AliasManager) -> int:
        if alias == -1: return -1
        if alias == None: return alias_manager.aliases[None]
        alias_l: str = alias.lower()

        # find alias from alias list
        for _alias in alias_manager.aliases.keys():
            if _alias == None: continue
            if alias_l == _alias.lower(): return alias_manager.aliases[_alias]

        # find alias from available table names
        for idx, table in self.tables.items():
            if alias_l == table.name.lower(): return idx

        raise Exception('Not found alias {}'.format(alias))

    def table_id(self, name: str) -> int:
        name_l = name.lower()
        for idx, table in self.tables.items():
            if table.name.lower() == name_l: return idx

        raise Exception('No table_id for #{}'.format(name))

    def table(self, idx: int) -> Table:
        return self.tables[idx]

    def column(self, name: str, table_idx: int, alias_manager: AliasManager = None) -> Column:
        name = name.lower()
        for column in self.columns:
            if column.table_idx != table_idx: continue
            if column.name.lower() != name: continue
            return column

        # search the column from other available tables
        if alias_manager:
            available_table_ids: [int] = alias_manager.aliases.values()
            for column in self.columns:
                if column.table_idx not in available_table_ids: continue
                if column.name.lower() != name: continue
                return column

        raise Exception('No column for #{}({})'.format(name, table_idx))

    def column_by_idx(self, column_idx: int) -> Column:
        for column in self.columns:
            if column.column_idx == column_idx: return column

        raise Exception('No column for id={}'.format(column_idx))

    def scheme(self):
        db_path: str = SQL_PATH + self.db_dict['db_id'] + '/' + self.db_dict['db_id'] + '.sqlite'
        return Schema(get_schema(db_path))

    def to_on_query(self, table1_idx: int, table2_idx: int, alias_manager: AliasManager) -> str:
        alias1: str = alias_manager.alias(table1_idx)
        alias2: str = alias_manager.alias(table2_idx)
        for (col1_idx, col2_idx) in self.db_dict['foreign_keys'].items():
            col1 = self.column_by_idx(col1_idx)
            col2 = self.column_by_idx(col2_idx)
            if col1.table_idx == table1_idx and col2.table_idx == table2_idx:
                return 'ON {}.{} = {}.{}'.format(alias1, col1.name, alias2, col2.name)
            if col1.table_idx == table2_idx and col2.table_idx == table1_idx:
                return 'ON {}.{} = {}.{}'.format(alias1, col2.name, alias2, col1.name)

        raise Exception('No foreign_key pair for table ids ({}, {})'.format(table1_idx, table2_idx))

# %%

# %%
