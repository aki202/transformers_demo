# %%
from generator.alias_manager import AliasManager
from generator.db import DB
from generator.column import Column

class Join:
    def __init__(self, base_col: Column, target_col: Column):
        self.base_col: Column = base_col
        self.target_col: Column = target_col

    def to_query(self, db: DB, alias_manager: AliasManager) -> str:
        join_table: str = db.table_name(self.target_col.table_idx)
        base_alias: str = alias_manager.alias(self.base_col.table_idx)
        target_alias: str = alias_manager.alias(self.target_col.table_idx)

        return 'JOIN {} AS {} ON {}.{} = {}.{}'.format(
            join_table, target_alias, base_alias, self.base_col.name, target_alias, self.target_col.name
        )

# %%
if __name__ == '__main__':
    db = DB({
        'column_names_original': [
            [-1, '*'],
            [0, 'id'],
            [0, 'customer_id'],
            [1, 'id'],
            [1, 'name'],
        ],
        'table_names_original': ['Invoices', 'Customers']
    })
    am1 = AliasManager()
    am1.add(None, 0)
    am1.add('T1', 0)
    am1.add('T2', 1)
    join1 = Join(Column('customer_id', 2, 0), Column('id', 3, 1))
    print(join1.to_query(db, am1))

# %%
