# coding=utf-8
import json

import psycopg2
import psycopg2.extras
import psycopg2.extensions
from datetime import datetime
import time


def connect_dev_db():
    conn = psycopg2.connect(host='mesoor-dev.c1l6advd1fez.rds.cn-north-1.amazonaws.com.cn',
                            user='mesoor',
                            password='k4j%Te#hEqpVHABJKtF2',
                            database='mesoor')
    # conn.autocommit = True
    return conn


def connect_prod_db():
    conn = psycopg2.connect(host='mesoor.c1l6advd1fez.rds.cn-north-1.amazonaws.com.cn',
                            user='mesoor',
                            password='k4j%Te#hEqpVHABJKtF2',
                            database='mesoor')
    # conn.autocommit = True
    return conn


def connect_db():
    # return connect_dev_db()
    return connect_prod_db()


def update_city(schema, step=5000):
    conn = connect_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    update_sql = """UPDATE {}.city SET city = city;""".format(schema)

    start_time = datetime.now()
    print(update_sql)
    cur.execute(update_sql)
    conn.commit()
    print(datetime.now() - start_time)

    cur.close()
    conn.close()


def update_resume_version(schema, step=5000):
    conn = connect_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute('SELECT MAX(id) as id FROM {}.candidate;'.format(schema))
    row = cur.fetchone()
    max_id = row[0]
    print('max_id', max_id)
    if not max_id:
        print('no max_id found: ', schema)
        return

    update_sql = """UPDATE {}.candidate
                    SET resume = jsonb_set(resume, '{{version}}', to_jsonb(COALESCE(resume ->> 'version', '0')::INT + 1))
                    WHERE id >= {} AND id <= {};"""

    for start in range(1, max_id, step):
        start_time = datetime.now()

        end = start + step - 1
        print(start, end)
        sql = update_sql.format(schema, start, end)
        print(sql)
        cur.execute(sql)
        conn.commit()

        print(datetime.now() - start_time)

        if max_id > step:
            time.sleep(40)

    cur.close()
    conn.close()


def update_job_version(schema, step=5000):
    conn = connect_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute('SELECT MAX(id) as id FROM {}.job;'.format(schema))
    row = cur.fetchone()
    max_id = row[0]
    print('max_id', max_id)
    if not max_id:
        print('no max_id found: ', schema)
        return

    update_sql = """UPDATE {}.job SET version = version + 1 WHERE id >= {} AND id <= {};"""

    for start in range(1, max_id, step):
        start_time = datetime.now()

        end = start + step - 1
        print(start, end)
        sql = update_sql.format(schema, start, end)
        print(sql)
        cur.execute(sql)
        conn.commit()

        print(datetime.now() - start_time)

        if max_id > step:
            time.sleep(60)

    cur.close()
    conn.close()


def update_job_candidate_version(schema, step=5000):
    conn = connect_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute('SELECT MAX(id) as id FROM {}.job_candidate;'.format(schema))
    row = cur.fetchone()
    max_id = row[0]
    print('max_id', max_id)
    if not max_id:
        print('no max_id found: ', schema)
        return

    update_sql = """UPDATE {}.job_candidate SET version = version + 1 WHERE id >= {} AND id <= {};"""

    for start in range(1, max_id, step):
        start_time = datetime.now()

        end = start + step - 1
        print(start, end)
        sql = update_sql.format(schema, start, end)
        print(sql)
        cur.execute(sql)
        conn.commit()

        print(datetime.now() - start_time)

    cur.close()
    conn.close()


def update_tenant(tenant):
    print('start to update tenant: ', tenant)

    update_city(tenant)
    update_job_version(tenant)
    update_resume_version(tenant)
    update_job_version(tenant)
    update_job_candidate_version(tenant)

    print('tenant: ', tenant, 'updated')


def get_tenants():
    tenants = []
    with open('tenants.txt') as f:
        for l in f:
            tenants.append(l.strip())
    return tenants


if __name__ == '__main__':
    start_point = datetime.now()

    # update_job_version('tenant_neitui')
    # update_job_version('tenant_qushixi')

    # update_resume_version('tenant_neitui')
    # update_resume_version('tenant_qushixi')

    # update_job_candidate_version('tenant_qushixi')
    # update_tenant('tenant_neitui')
    # update_tenant('tenant_jobs')

    tenants = get_tenants()
    # tenants = ['tenant_neitui', 'tenant_jobs']
    # tenants = ['tenant_qushixi']

    # update all tenants
    for tenant in tenants:
        update_tenant(tenant)
        time.sleep(1)

    # db_ver()

    # update ocean
    update_resume_version('ocean')

    print(datetime.now() - start_point)
