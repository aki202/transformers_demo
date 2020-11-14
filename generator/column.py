# %%
class Column:
    def __init__(self, name: str, column_idx: int, table_idx: int = None):
        '''
        column_idx: -1 => count(*)など、対象のテーブルが特定されない
        '''
        self.name = name
        self.column_idx = column_idx
        self.table_idx = table_idx

    def __str__(self):
        return '{}(tbl_id={}, col_id={})'.format(self.name, self.table_idx, self.column_idx)
