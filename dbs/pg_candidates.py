# coding=utf-8
import json

import psycopg2
import psycopg2.extras

from dbs.resume_struct import normalize_missing_values

conn = psycopg2.connect(host='mesoor-dev.c1l6advd1fez.rds.cn-north-1.amazonaws.com.cn',
                        user='mesoor',
                        password='k4j%Te#hEqpVHABJKtF2',
                        database='mesoor')


def select():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM ocean.candidate LIMIT 100;')

    rows = cur.fetchall()
    records = []
    for row in rows:
        record = {}

        # resume
        resume = row['resume']
        basic = resume['basic']
        basic['location'] = {"id": 3703, "city": "淄博市", "province": "山东省"}
        resume['skills'] = ['java', 'python', 'scala', 'php']
        resume['status'] = {
            "salary_low": 10000,
            "salary_high": 15000,
            "professional_title": 3
        }
        resume['provide'] = {
            "timing": {
                "period": 15,
                "startAt": "2017-11-16T07:00:07.829Z",
                "daysPerWeek": 3
            }
        }

        print(row['id'])
        print(resume['expectation'])

        # resume['expectation'] = {
        #                             "exclude": {
        #                                 "companies": [
        #                                     "五晨寺",
        #                                     "仙塞学院",
        #                                     "暗影之地"
        #                                 ],
        #                                 "scale_low": 1,
        #                                 "industries": [
        #                                     "工程"
        #                                 ],
        #                                 "scale_high": 100,
        #                                 "work_types": [
        #                                     2
        #                                 ],
        #                                 "fin_stage_low": 2,
        #                                 "fin_stage_high": 5
        #                             },
        #                             "work_time": 30,
        #                             "industries": [
        #                                 "锻造",
        #                                 "珠宝",
        #                                 "烹饪"
        #                             ],
        #                             "salary_low": 15000,
        #                             "work_types": [
        #                                 0
        #                             ],
        #                             "locationIds": [
        #                                 3101
        #                             ],
        #                             "salary_high": 20000,
        #                             "job_categories": [
        #                                 "00150345"
        #                             ]
        #                         },
        # resume['update_date'] = "2017-11-20T07:00:07.829Z"
        # resume['languages_set'] = [
        #     {
        #         "exams": [
        #             {
        #                 "score": 600,
        #                 "name": "四级"
        #             }
        #         ],
        #         "name": "鱼人语"
        #     }
        # ]

        resume = normalize_missing_values(resume)
        print(resume)

        record['resume'] = resume

        # others
        record['industry'] = row['industry']
        record['years'] = row['years']
        record['degree'] = row['degree']
        record['passcode'] = row['passcode']
        record['status'] = row['status']
        record['createAt'] = row['createAt']
        record['updateAt'] = row['updateAt']
        record['version'] = row['version']
        record['location'] = row['location']
        record['creator'] = row['creator']

        # print(years, passcode)
        records.append(record)

        print()

    # json.dump(records, open('records.json', 'w'), ensure_ascii=False)

    cur.close()
    # conn.close()

    return records


def insert():
    records = select()
    sql = """INSERT INTO tenant_neitui.candidate (industry, years, degree, resume, passcode, 
              status, "createAt", "updateAt", version, location, creator) 
             VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    # for record in records:
    #     cur = conn.cursor()
    #     print(record['location'], record['creator'])
    #     cur.execute(sql, (record['industry'], record['years'], record['degree'],
    #                       json.dumps(record['resume'], ensure_ascii=False), record['passcode'],
    #                       record['status'], record['createAt'], record['updateAt'], record['version'],
    #                       record['location'], record['creator']))
    #     conn.commit()


if __name__ == '__main__':
    # db_ver()
    # select()
    insert()
