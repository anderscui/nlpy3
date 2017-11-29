# coding=utf-8
import json

import psycopg2
import psycopg2.extras

from dbs.resume_struct import normalize_missing_values

conn = psycopg2.connect(host='mesoor-dev.c1l6advd1fez.rds.cn-north-1.amazonaws.com.cn',
                        user='mesoor',
                        password='k4j%Te#hEqpVHABJKtF2',
                        database='mesoor')
conn.autocommit = True


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
    cur.execute('SELECT * FROM {}.job ORDER BY "updateAt" DESC OFFSET 0 LIMIT 1000;'.format(schema))

    rows = cur.fetchall()
    records = []
    for row in rows:
        location_ids = row['location_ids']
        if location_ids:
            new_ids = [update_code(loc) for loc in location_ids]
            print(row['id'], location_ids, new_ids)
            records.append((json.dumps(new_ids, ensure_ascii=False), row['id']))

    cur.close()

    print(len(records))
    return records


def update(schema):
    records = select(schema)
    sql = "UPDATE {}.job SET location_ids = %s, version = 10 WHERE id = %s".format(schema)

    # cur = conn.cursor()
    # for record in records:
    #     print(record)
    #     cur.execute(sql, record, record[0])
    # conn.commit()
    #
    cur = conn.cursor()
    psycopg2.extras.execute_batch(cur, sql, records, page_size=50)
    conn.commit()


if __name__ == '__main__':
    # db_ver()
    # select()
    # update('tenant_jobs')
    update('tenant_neitui')
