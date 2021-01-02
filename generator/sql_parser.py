# %%
'''
- [x] select
- [x] from
- [x] join
- [ ] where
- [ ] group
- [ ] having
- [ ] order
- [ ] limit
- [ ] union
- [ ] except
- [ ] intersect
'''

import json
from generator.db_manager import DBManager
from generator.db import DB
from generator.alias_manager import AliasManager
from generator.table import Table
from generator.column import Column
from generator.join import Join
from generator.select_column import SelectColumn, parse_to_select_column
from generator.where import Where, parse_to_where
from generator.splitter import split
from pprint import pprint as pp
import re

join_pattern = re.compile(r'''
    JOIN\s+
    (?P<table>[^\s]+)\s*
    (?:
        AS\s+
       (?P<alias>[^\s]+)
    )?
''', re.IGNORECASE + re.VERBOSE)

on_pattern = re.compile(r'''
    (?P<alias1>[^\s]+)\.(?P<col1>[^\s]+)\s+=\s+
    (?P<alias2>[^\s]+)\.(?P<col2>[^\s]+)
''', re.IGNORECASE + re.VERBOSE)

# %%
class SqlParser:
    def __init__(self, sql_dict: dict, db: DB):
        self.query: str = sql_dict['query']
        self.query_parts: { str: str } = split(self.query)
        self.sql_g: dict = sql_dict['sql']
        self.db: DB = db
        self.alias_manager = AliasManager()

        self.from_table: Table = None
        self.joins: [Join] = [] # counts 0-3
        self.global_distinct: bool = False
        self.select_columns: [SelectColumn] = []
        self.wheres: [Where] = []

        self.parse_from_table()
        self.parse_join_tables()
        self.parse_select_columns()
        # self.parse_wheres()

    def __str__(self) -> str:
        out = '{}\n'.format(self.query)
        global_distinct_disp: str = 'using global distinct' if self.global_distinct else ''
        out += 'SELECT: {}\n'.format(global_distinct_disp)
        for select_column in self.select_columns:
            out += '\t{}\n'.format(select_column)
        out += 'FROM: {}\n'.format(self.from_table.name)
        out += 'JOIN:\n'
        for join in self.joins:
            out += '\t{}\n'.format(join.to_query(self.db, self.alias_manager))
        out += 'WHERE: \n'
        for where in self.wheres:
            out += '\t{}\n'.format(where)

        return out

    def to_query(self) -> str:
        # create SELECT clause
        query = 'SELECT '
        selects: [str] = [select_column.to_query(self.alias_manager) for select_column in self.select_columns]
        query += ', '.join(selects)

        # create FROM clause
        query += ' FROM {}'.format(self.from_table.name)
        if len(self.alias_manager) > 1:
            alias: str = self.alias_manager.alias(self.from_table.idx)
            if alias.lower() != self.from_table.name.lower(): # table name and alias are different
                query += ' AS {}'.format(self.alias_manager.alias(self.from_table.idx))

        # create JOINs clause
        join_queries: [str] = [join.to_query(self.db, self.alias_manager) for join in self.joins]
        if len(join_queries) > 0:
            query += ' '
            query += ' '.join(join_queries)

        # create WHERE clause
        if len(self.query_parts['where']) > 0:
            query += ' ' + self.query_parts['where']

        # create GROUP clause
        if len(self.query_parts['group']) > 0:
            query += ' ' + self.query_parts['group']

        # create GROUP clause
        if len(self.query_parts['having']) > 0:
            query += ' ' + self.query_parts['having']

        # create ORDER clause
        if len(self.query_parts['order']) > 0:
            query += ' ' + self.query_parts['order']

        # create LIMIT clause
        if len(self.query_parts['limit']) > 0:
            query += ' ' + self.query_parts['limit']

        return query

    def parse_from_table(self) -> None:
        reg = r'FROM +(?P<table>[^ ]+) *(?:AS +(?P<alias>[^ ]+))?'
        select_matches: re.Match = re.search(reg, self.query_parts['from'], flags=re.IGNORECASE)
        hit: {str: str} = select_matches.groupdict()
        table_name = hit['table']
        table_idx = self.db.table_id(table_name)
        self.from_table = Table(table_name, table_idx)
        self.alias_manager.add(None, table_idx)

        # there is a alias
        if hit['alias']:
            self.alias_manager.add(hit['alias'], table_idx)
        else:
            self.alias_manager.add(table_name, table_idx)

    def parse_join_tables(self) -> None:
        join_matches: [re.Match] = join_pattern.finditer(self.query_parts['join'])
        on_matches: [re.Match] = on_pattern.finditer(self.query_parts['join'])

        on_hits: [{str: str}] = []
        for match in on_matches:
            hit = match.groupdict()
            on_hits.append({
                'alias1': hit['alias1'],
                'col1':   hit['col1'],
                'alias2': hit['alias2'],
                'col2':   hit['col2']
            })

        for match in join_matches:
            hit = match.groupdict()
            target_table_name = hit['table']
            target_alias = hit['alias'] or target_table_name
            target_table_idx = self.db.table_id(target_table_name)

            self.alias_manager.add(target_alias, target_table_idx)

            '''
            for on_hit in on_hits: print('on_hit', on_hit)
            print('target_table_name={}, target_alias={}, target_table_idx={}'.format(
                target_table_name, target_alias, target_table_idx
            ))
            print("table_id(on_hit['alias1'])", self.alias_manager.table_id(on_hit['alias1']))
            print("table_id(on_hit['alias2'])", self.alias_manager.table_id(on_hit['alias2']))
            '''

            # find the corresponding on-clause
            for on_hit in on_hits:
                if (on_hit['alias1'].lower() == target_alias.lower() and
                    self.alias_manager.table_id(on_hit['alias2']) != None
                    ):
                    base_table_idx = self.db.table_id_by_alias(on_hit['alias2'], self.alias_manager)
                    base_col = self.db.column(on_hit['col2'], base_table_idx)
                    target_col = self.db.column(on_hit['col1'], target_table_idx)
                    break
                if (on_hit['alias2'].lower() == target_alias.lower() and
                    self.alias_manager.table_id(on_hit['alias1']) != None
                    ):
                    base_table_idx = self.db.table_id_by_alias(on_hit['alias1'], self.alias_manager)
                    base_col = self.db.column(on_hit['col1'], base_table_idx)
                    target_col = self.db.column(on_hit['col2'], target_table_idx)
                    break
            join = Join(base_col, target_col)
            self.joins.append(join)

    def parse_select_columns(self) -> None:
        matches: re.Match = re.search(r'SELECT +(?P<dis>DISINCT +)?(?P<cols>.+)',
            self.query_parts['select'], flags=re.IGNORECASE)
        hit = matches.groupdict()
        #raw_matched: str = matches[1].strip()

        # wheather the global distinct is used
        if hit['dis']: self.global_distinct = True

        # wheather
        raw_cols: [str] = hit['cols'].split(',')
        for raw_col in raw_cols:
            self.select_columns.append(parse_to_select_column(raw_col, self.db, self.alias_manager))

    def parse_wheres(self) -> None:
        # TODO: implement
        matches: re.Match = re.search(r'WHERE +(?P<where>.+) *', self.query_parts['where'], flags=re.IGNORECASE)
        hit = matches.groupdict()

        # wheather
        for where_raw in hit['where'].split(','):
            wheare = parse_to_where(where_raw.strip(), self.db, self.alias_manager)
            self.wheres.append(wheare)

    def condition_values(self) -> [str]:
        values: [any] = []

        for w in re.findall(r'"(.+?)"', self.query_parts['where'], re.IGNORECASE):
            values.append(w)

        for w in re.findall(r"'(.+?)'", self.query_parts['where'], re.IGNORECASE):
            values.append(w)

        for w in re.findall(r' (\d{2,}?)', self.query_parts['where'], re.IGNORECASE):
            values.append(w)

        return values

    '''
    def available_table_names(self):
        tables: [str] = [self.from_table.name]

        for join in self.joins:
            table: Table = self.db.table_name(join.target_col.table_idx)
            tables.append(table.name)

        return tables
    '''

# %%
if __name__ == '__main__':
    train_spider_json = json.load(open('data/spider/train_spider.json'))
    sql_dict = train_spider_json[520]
    db_manager = DBManager('data/spider/tables.json')
    db = db_manager.create_db(sql_dict['db_id'])
    parser = SqlParser(sql_dict, db)
    print(parser)
    print(parser.to_query())
    print(parser.condition_values())

# %%

# %%
'''
- tables
    0 'customers'
    1 'invoices'
    2 'orders'
    3 'products'
    4 'order items'
    5 'shipments'
    6 'shipment items'
- columns
    0 [-1, '*'],
    1 [0, 'customer_id'],
    2 [0, 'customer_name'],
    3 [0, 'customer_details'],
    4 [1, 'invoice_number'],
    5 [1, 'invoice_date'],
    6 [1, 'invoice_details'],
    7 [2, 'order_id'],
    8 [2, 'customer_id'],
    9 [2, 'order_status'],
    10 [2, 'date_order_placed'],
    11 [2, 'order_details'],
    12 [3, 'product_id'],
    13 [3, 'product_name'],
    14 [3, 'product_details'],
    15 [4, 'order_item_id'],
    16 [4, 'product_id'],
    17 [4, 'order_id'],
    18 [4, 'order_item_status'],
    19 [4, 'order_item_details'],
    20 [5, 'shipment_id'],
    21 [5, 'order_id'],
    22 [5, 'invoice_number'],
    23 [5, 'shipment_tracking_number'],
    24 [5, 'shipment_date'],
    25 [5, 'other_shipment_details'],
    26 [6, 'shipment_id'],
    27 [6, 'order_item_id']
- foreign keys [column_id, column_id], (table_id, table_id)
    [8, 1], (2, 0)
    [16, 12], (4, 3)
    [17, 7], (4, 2)
    [22, 4], (5, 1)
    [21, 7], (5, 2)
    [26, 20], (6, 5)
    [27, 15], (6, 4)

from 0: FROM customers AS T1
join 2: JOIN orders AS T2 ON T1.customer_id = T2.customer_id    using 0 = 2 : [8, 1], (2, 0)
join 4: JOIN order_items AS T3 ON T2.order_id = T3.order_id     using 2 = 3 : [17, 7], (4, 2)
join 3: JOIN products AS T4 ON T3.product_id = T4.product_id    using 4 = 3 : [16, 12], (4, 3)

T1: 0 customers
T2: 2 orders
T3: 4 order_items
T4: 3 products
'''
