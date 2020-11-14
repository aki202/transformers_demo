# %%
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
from pprint import pprint as pp
from generator.db import DB

# %%
class DBManager:
    def __init__(self, tables_json_path: str):
        self.tables_json_path = tables_json_path
        self.dbs: {str: dict} = {}

        self.__load_all_dbs__()

    def __load_all_dbs__(self) -> None:
        dbs = json.load(open(self.tables_json_path))
        for db in dbs: self.dbs[db['db_id']] = db

    def db_dict(self, db_id: str) -> dict:
        return self.dbs[db_id]

    def create_db(self, db_id: str) -> DB:
        return DB(self.db_dict(db_id))

# %%
if __name__ == '__main__':
    db_manager = DBManager(tables_json_path='data/spider/tables.json')
    db_dict = db_manager.db_dict('department_management')
    pp(db_dict)

# %%
