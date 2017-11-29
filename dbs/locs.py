# coding=utf-8
from collections import defaultdict

import pandas as pd
import json
# import MySQLdb

LOCS_FILE = 'locs_full.json'


DDL = """CREATE TABLE location_all
(
  code VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  short_name VARCHAR(255) NOT NULL,
  geo VARCHAR(255) NOT NULL,
  level VARCHAR(255) NOT NULL,
  parent_code VARCHAR(255) NOT NULL,
  constraint idx_code
    unique (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
"""


def add_padding(i, width):
    return str(i).rjust(width, '0')


def show_all_locs():
    all_locs = json.load(open(LOCS_FILE))
    return all_locs


if __name__ == '__main__':
    locs_full = show_all_locs()
    locs_full.append({'province_id': '81', 'province_name': '香港特别行政区', 'province_short_name': '香港', 'province_geo': '22.293586,114.186124',
                     'city_id': '8101', 'city_name': '香港特别行政区', 'city_short_name': '香港', 'city_geo': '22.293586,114.186124',
                     'county_id': '810101', 'county_name': None, 'county_short_name': None, 'county_geo': '22.293586,114.186124'})
    locs_full.append({'province_id': '82', 'province_name': '澳门特别行政区', 'province_short_name': '澳门', 'province_geo': '22.204118,113.557519',
                     'city_id': '8201', 'city_name': '澳门特别行政区', 'city_short_name': '澳门', 'city_geo': '22.204118,113.557519',
                     'county_id': '820101', 'county_name': None, 'county_short_name': None, 'county_geo': '22.204118,113.557519'})


    SQL = """INSERT INTO location_all (province_id, province_name, province_short_name, province_geo, city_id, city_name, city_short_name, city_geo, county_id, county_name, county_short_name, county_geo)
             VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"""

    for loc in locs_full:
        sql = SQL.format(loc['province_id'], loc['province_name'], loc['province_short_name'], loc['province_geo'],
                         loc['city_id'], loc['city_name'], loc['city_short_name'], loc['city_geo'],
                         loc['county_id'], loc['county_name'], loc['county_short_name'], loc['county_geo'])


    # import MySQLdb
    # db = MySQLdb.connect('localhost', 'root', 'nadileaf', 'knowledge_db', charset='utf8', use_unicode=True)
    # cur = db.cursor()
    #
    SQL = """INSERT INTO location_all (province_id, province_name, province_short_name, province_geo, city_id, city_name, city_short_name, city_geo, county_id, county_name, county_short_name, county_geo)
                 VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"""
    for loc in locs_full:
        sql = SQL.format(loc['province_id'], loc['province_name'], loc['province_short_name'], loc['province_geo'],
                         loc['city_id'], loc['city_name'], loc['city_short_name'], loc['city_geo'],
                         loc['county_id'], loc['county_name'], loc['county_short_name'], loc['county_geo'])
        print(sql)
    #     cur.execute(sql)
    # db.commit()

    # locs_full = []
    # locs_geo = {}
    # for loc in locs_full:
    #     province_geo = None
    #     province_id = loc['province_id'] + '0000'
    #     if province_id in locs_geo:
    #         loc_geo = locs_geo[province_id]
    #         if loc_geo['latitude'] and loc_geo['longitude']:
    #             province_geo = '{},{}'.format(loc_geo['latitude'], loc_geo['longitude'])
    #     loc['province_geo'] = province_geo
    #
    #     city_geo = None
    #     city_id = loc['city_id'] + '00'
    #     # if city_id not in locs_geo:
    #     #     city_id = city_id[:2] + '0000'
    #     if city_id in locs_geo:
    #         loc_geo = locs_geo[city_id]
    #         if loc_geo['latitude'] and loc_geo['longitude']:
    #             city_geo = '{},{}'.format(loc_geo['latitude'], loc_geo['longitude'])
    #     loc['city_geo'] = city_geo
    #
    #     county_geo = None
    #     if loc['county_id'] in locs_geo:
    #         loc_geo = locs_geo[loc['county_id']]
    #         county_geo = '{},{}'.format(loc_geo['latitude'], loc_geo['longitude'])
    #     loc['county_geo'] = county_geo

    # s = """INSERT INTO knowledge_db.job_category_wanglian_master
    #         (job_3l_num, job_3l_name_cn, job_2l_num, job_2l_name_cn, job_1l_num, job_1l_name_cn)
    #         VALUES('{job_3l_num}', '{job_3l_name_cn}', '{job_2l_num}', '{job_2l_name_cn}', '{job_1l_num}', '{job_1l_name_cn}')""".format(**rows[0])
    # print(s)
