# %%
from generator.sql_parser import SqlParser
from generator.db_manager import DBManager
from generator.splitter import split
import random
import json
import sys
import re

invalid_queries: [str] = [
    # unknown
    'SELECT T2.Lname FROM DEPARTMENT AS T1 JOIN FACULTY AS T2 ON T1.DNO  =  T3.DNO JOIN MEMBER_OF AS T3 ON T2.FacID  =  T3.FacID WHERE T1.DName  =  "Computer Science"',
    'SELECT count(*) FROM STUDENT AS T1 JOIN VOTING_RECORD AS T2 ON T1.StuID  =  Class_Senator_Vote WHERE T1.Sex  =  "M" AND T2.Election_Cycle  =  "Fall"',
    'SELECT count(*) FROM STUDENT AS T1 JOIN VOTING_RECORD AS T2 ON T1.StuID  =  Class_Senator_Vote WHERE T1.city_code  =  "NYC" AND T2.Election_Cycle  =  "Spring"',
    'SELECT avg(T1.Age) FROM STUDENT AS T1 JOIN VOTING_RECORD AS T2 ON T1.StuID  =  SECRETARY_Vote WHERE T1.city_code  =  "NYC" AND T2.Election_Cycle  =  "Spring"',
    'SELECT avg(T1.Age) FROM STUDENT AS T1 JOIN VOTING_RECORD AS T2 ON T1.StuID  =  SECRETARY_Vote WHERE T1.Sex  =  "F" AND T2.Election_Cycle  =  "Spring"',
    'SELECT T1.Name ,  T3.Visit_Date FROM Tourist_Attractions AS T1 JOIN VISITORS AS T2 JOIN VISITS AS T3 ON T1.Tourist_Attraction_ID  =  T3.Tourist_Attraction_ID AND T2.Tourist_ID  =  T3.Tourist_ID WHERE T2.Tourist_Details  =  "Vincent" OR T2.Tourist_Details  =  "Vivian"',
    # inverse T1 <=> T2
    'SELECT T2.first_name , T2.last_name FROM employees AS T1 JOIN employees AS T2 ON T1.id = T2.reports_to WHERE T1.first_name = "Nancy" AND T1.last_name = "Edwards";',
    'SELECT T2.first_name , T2.last_name ,  count(T1.reports_to) FROM employees AS T1 JOIN employees AS T2 ON T1.reports_to = T2.id GROUP BY T1.reports_to ORDER BY count(T1.reports_to) DESC LIMIT 1;',
    'SELECT T2.name ,  T3.name FROM wedding AS T1 JOIN people AS T2 ON T1.male_id  =  T2.people_id JOIN people AS T3 ON T1.female_id  =  T3.people_id WHERE T1.year  >  2014',
    'SELECT T4.name FROM wedding AS T1 JOIN people AS T2 ON T1.male_id  =  T2.people_id JOIN people AS T3 ON T1.female_id  =  T3.people_id JOIN church AS T4 ON T4.church_id  =  T1.church_id WHERE T2.age  >  30 OR T3.age  >  30',
    'SELECT T2.employee_name ,  T3.employee_name FROM Documents_to_be_destroyed AS T1 JOIN Employees AS T2 ON T1.Destruction_Authorised_by_Employee_ID = T2.employee_id JOIN Employees AS T3 ON T1.Destroyed_by_Employee_ID = T3.employee_id;',
    "SELECT DISTINCT T4.name FROM PersonFriend AS T1 JOIN Person AS T2 ON T1.name  =  T2.name JOIN PersonFriend AS T3 ON T1.friend  =  T3.name JOIN PersonFriend AS T4 ON T3.friend  =  T4.name WHERE T2.name  =  'Alice' AND T4.name != 'Alice'",
    # multiple join conditions
    'SELECT T2.faculty FROM campuses AS T1 JOIN faculty AS T2 ON T1.id  =  t2.campus JOIN degrees AS T3 ON T1.id  =  t3.campus AND t2.year  =  t3.year WHERE t2.year  =  2002 ORDER BY t3.degrees DESC LIMIT 1',
    'SELECT count(*) ,  T1.blockfloor FROM BLOCK AS T1 JOIN room AS T2 ON T1.blockfloor  =  T2.blockfloor AND T1.blockcode  =  T2.blockcode GROUP BY T1.blockfloor',
    'SELECT count(*) ,  T1.blockcode FROM BLOCK AS T1 JOIN room AS T2 ON T1.blockfloor  =  T2.blockfloor AND T1.blockcode  =  T2.blockcode GROUP BY T1.blockcode',
    'SELECT T4.instrument FROM Performance AS T1 JOIN Band AS T2 ON T1.bandmate  =  T2.id JOIN Songs AS T3 ON T3.SongId  =  T1.SongId JOIN Instruments AS T4 ON T4.songid  =  T3.songid AND T4.bandmateid  =  T2.id WHERE T2.lastname  =  "Heilo" AND T3.title  =  "Le Pop"',
    'SELECT T4.instrument FROM Performance AS T1 JOIN Band AS T2 ON T1.bandmate  =  T2.id JOIN Songs AS T3 ON T3.SongId  =  T1.SongId JOIN Instruments AS T4 ON T4.songid  =  T3.songid AND T4.bandmateid  =  T2.id WHERE T2.lastname  =  "Heilo" AND T3.title  =  "Badlands"',
    # using multiple T1
    'SELECT T1.title ,  T1.director FROM Movie AS T1 JOIN Movie AS T2 ON T1.director  =  T2.director WHERE T1.title != T2.title ORDER BY T1.director ,  T1.title',
    'SELECT T1.title ,  T1.year FROM Movie AS T1 JOIN Movie AS T2 ON T1.director  =  T2.director WHERE T1.title != T2.title',
    'SELECT DISTINCT t1.product_name FROM products AS t1 JOIN complaints AS t2 ON t1.product_id  =  t2.product_id JOIN customers AS t3 GROUP BY t3.customer_id ORDER BY count(*) LIMIT 1',
    # invalid join table
    "SELECT DISTINCT T1.lname FROM Faculty AS T1 JOIN Faculty_participates_in AS T2 ON T1.facID  =  T2.facID JOIN activity AS T3 ON T2.actid  =  T2.actid WHERE T3.activity_name  =  'Canoeing' OR T3.activity_name  =  'Kayaking'",
]
# ---pendinng---
# same alias as table name
# SELECT Addresses.address_details FROM Addresses JOIN Documents_Mailed ON Documents_Mailed.mailed_to_address_id = Addresses.address_id WHERE document_id = 4;
# SELECT count(*) FROM Restaurant JOIN Type_Of_Restaurant ON Restaurant.ResID =  Type_Of_Restaurant.ResID JOIN Restaurant_Type ON Type_Of_Restaurant.ResTypeID = Restaurant_Type.ResTypeID GROUP BY Type_Of_Restaurant.ResTypeID HAVING Restaurant_Type.ResTypeName = 'Sandwich'
# SELECT sum(Spent) FROM Student JOIN Visits_Restaurant ON Student.StuID = Visits_Restaurant.StuID WHERE Student.Fname = "Linda" AND Student.Lname = "Smith";
#

class Generate:
    def __init__(self):
        self.spider_json: [dict] = json.load(open('data/spider/train_spider.json'))
        self.db_manager = DBManager('data/spider/tables.json')

    def sample_sql_dict(self) -> dict:
        size = len(self.spider_json)
        index = random.randint(0, size)
        return self.spider_json[index]

    def generate_one(self) -> None:
        sql_dict = self.sample_sql_dict()
        self.generate_one_by_sql_dict(sql_dict)

    def validate(self, sql_dict: dict):
        tokens: [str] = [tok.lower() for tok in sql_dict['query_toks']]
        invalids: [str] = ['intersect', 'union', 'except']
        invalid_dbs: [str] = ['assets_maintenance']
        for invalid in invalids:
            if invalid in tokens: return False

        query_parts: { str: str } = split(sql_dict['query'])
        if ' - ' in query_parts['select']: return False
        if ' + ' in query_parts['select']: return False
        if 'select' in query_parts['from']: return False
        if 'SELECT' in query_parts['from']: return False
        if len(query_parts['join']) > 1:
            if ' on ' not in query_parts['join'] and ' ON ' not in query_parts['join']: return False
        if ('skip', True) in sql_dict: return False

        # using an invalid db
        if sql_dict['db_id'] in invalid_dbs: return False

        # using in invalid query
        if sql_dict['query'] in invalid_queries: return False

        return True

    def generate_one_by_sql_dict(self, sql_dict: dict) -> None:
        db = self.db_manager.create_db(sql_dict['db_id'])
        parser = SqlParser(sql_dict, db)
        return parser.to_query()
        #print('       to query: {}'.format(parser.to_query()))

# %%
# # check if the gold and generated queries are same
# if __name__ == '__main__':
#     generator = Generate()

#     counts = {
#         'ok': 0,
#         'ng': 0
#     }

#     # sql_dict = generator.spider_json[6859]
#     # print('      org query: {}'.format(sql_dict['query']))
#     # generator.generate_one_by_sql_dict(sql_dict)
#     # sys.exit()

#     for idx in range(len(generator.spider_json)):
#         sql_dict = generator.spider_json[idx]
#         print('[{}] original: {}'.format(idx, sql_dict['query']))
#         if not generator.validate(sql_dict):
#             print('invalid sql eury')
#             counts['ng'] += 1
#             continue
#         counts['ok'] += 1
#         gen_query: str = generator.generate_one_by_sql_dict(sql_dict)
#         print('       to query: {}'.format(gen_query))

#         comp1: str = sql_dict['query'].lower().replace(';', '')
#         comp1 = re.sub(r' ', '', comp1)
#         comp2: str = gen_query.lower().replace(';', '')
#         comp2 = re.sub(r' ', '', comp2)
#         if comp1 == comp2:
#             print('equal!')
#         else:
#             print('unequal!')
#             print(comp1)
#             print(comp2)
#             breakpoint()
#     print(counts)

# %%
# check if the specified sql_dict could be parsed
if __name__ == '__main__':
    from generator.query_alter import QueryAlter

    generator = Generate()

    sql_dict = generator.spider_json[6859]
    db = generator.db_manager.create_db(sql_dict['db_id'])
    parser = SqlParser(sql_dict, db)

    query_alter = QueryAlter(sql_dict)
    query_alter.alter()


# %%
