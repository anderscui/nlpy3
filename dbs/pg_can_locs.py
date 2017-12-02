# coding=utf-8
import json
import logging

import psycopg2
import psycopg2.extras
import psycopg2.extensions
from datetime import datetime

# from psycopg2 import sql


class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger = logging.getLogger('sql_debug')
        logger.info(self.mogrify(sql, args))

        try:
            psycopg2.extensions.cursor.execute(self, sql, args)
        except Exception as exc:
            logger.error("%s: %s" % (exc.__class__.__name__, exc))
            raise


conn = psycopg2.connect(host='mesoor-dev.c1l6advd1fez.rds.cn-north-1.amazonaws.com.cn',
                        user='mesoor',
                        password='k4j%Te#hEqpVHABJKtF2',
                        database='mesoor')
# conn.autocommit = True
# psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)


def update_code(code):
    cities = {1101: 110000,
              1201: 120000,
              3101: 310000,
              5001: 500000,
              5422: 540500,
              6522: 650500,
              10101: 810000,
              10201: 820000}
    if code in cities:
        return cities[code]
    return code * 100 if code < 100000 else code


def select(schema):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM {}.candidate ORDER BY "updateAt" DESC OFFSET 0 LIMIT 5000;'.format(schema))

    rows = cur.fetchall()
    records = []
    for row in rows:
        resume = row['resume']
        if resume and 'expectation' in resume and 'locationIds' in resume['expectation']:
            loc_ids = resume['expectation']['locationIds']
            if loc_ids:
                new_ids = [update_code(loc) for loc in loc_ids]
                print(row['id'], loc_ids, new_ids)
                resume['expectation']['locationIds'] = new_ids
                records.append((json.dumps(resume, ensure_ascii=False), row['id']))
                # records.append((resume, row['id']))

    cur.close()

    print(len(records))
    return records


def update(schema):
    records = select(schema)
    sql_stat = "UPDATE {}.candidate SET resume = %s, version = version + 1 WHERE id = %s; ".format(schema)

    # sql = """UPDATE {}.candidate AS t SET resume = c.resume
    #          FROM (VALUES %s) AS c(resume, id)
    #          WHERE t.id = c.id;""".format(schema)

    print(sql_stat)

    # values = [({'v': '5384332'}, 1), ({'v': '6031892'}, 2)]
    # print(values)

    start = datetime.now()

    sqls = []
    cur = conn.cursor()
    for record in records:
        query = cur.mogrify(sql_stat, record).decode()
        sqls.append(query)

    sqls = sqls * 50
    cur.execute('\n'.join(sqls))
    conn.commit()

    print(datetime.now() - start)

    # cur = conn.cursor()
    # psycopg2.extras.execute_batch(cur, sql, records, page_size=100)
    # psycopg2.extras.execute_values(cur, sql, values, page_size=100)
    # cur.execute(sql)
    # conn.commit()


if __name__ == '__main__':
    # db_ver()
    # select('tenant_neitui')
    update('tenant_neitui')
    # update('ocean')
