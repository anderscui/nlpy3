import fnmatch
import glob
import json
import re
import os

import random
import numpy as np
import pandas as pd

from collections import Counter, defaultdict

from toolz import first, last, take, drop, keyfilter, valfilter, itemfilter
from toolz.itertoolz import drop
from toolz.recipes import countby, partitionby

from elasticsearch_dsl.query import Match, Q

Q()


def json_load(file):
    return json.load(open(file))


def json_dump(obj, file):
    json.dump(obj, open(file, 'w'), ensure_ascii=False)


def read_lines(file):
    with open(file) as f:
        for l in f:
            yield l.strip()


def change_geo(lon_lat):
    if len(lon_lat) < 6:
        return lon_lat
    else:
        lon, lat = lon_lat.split(',')
        return '{},{}'.format(lat, lon)


def remove_prov_county_postfix(fullname):
    if fullname.endswith('市') or (fullname.endswith('县') and not fullname.endswith('自治县')):
        return fullname[:-1]
    elif fullname.endswith('自治县'):
        return fullname[:2]
    elif fullname.endswith('群岛'):
        return fullname[:-2]
    elif fullname.endswith('林区'):
        return fullname[:-2]
    else:
        return fullname


def update_code(code):
    cities = {1101: 110100,
              1201: 120100,
              3101: 310100,
              5001: 500100,
              5422: 542200,
              6522: 652200,
              10101: 810000,
              10201: 820000}
    if code in cities:
        return cities[code]
    return code * 100


prov_full = json_load('provinces_full.json')
city_full = json_load('cities_full.json')
prov_counties_full = json_load('prov_counties_full.json')

locs_all = json_load('locations_all.json')
cn = locs_all['districts'][0]
print(cn.keys())
provs = cn['districts']

cn_code = '100000'

prov_all = []
city_all = []
county_all = []
locations_all = []
locations_all.append((cn_code, '中华人民共和国', '中国', '39.915085,116.3683244', 'country', '0'))
for p in provs:
    pid = p['adcode']
    pname = p['name']
    p_short_id = pid[:2]
    pshort = prov_full[p_short_id][1]
    pcoor = change_geo(p['center'])
    prov_all.append((pid, pname, pshort, pcoor))
    locations_all.append((pid, pname, pshort, pcoor, p['level'], cn_code))

    cities = p['districts']
    for c in cities:
        cid = c['adcode']
        cname = c['name']
        cshort = None
        c_short_id = cid[:4]
        if c_short_id in city_full:
            cshort = city_full[c_short_id][1]
        elif cid in prov_counties_full:
            cshort = prov_counties_full[cid][1]
        else:
            cshort = cname
            print(cid, cname)
        ccoor = change_geo(c['center'])
        city_all.append((cid, cname, cshort, ccoor))
        locations_all.append((cid, cname, cshort, ccoor, c['level'], pid))

        counties = c['districts']
        for co in counties:
            if co['level'] != 'district':
                print(co)
                continue
            coid = co['adcode']
            coname = co['name']
            coshort = coname
            cocoor = change_geo(co['center'])
            county_all.append((coid, coname, coshort, cocoor))
            locations_all.append((coid, coname, coshort, cocoor, co['level'], cid))
            # locations_all.append((pid, pname, pshort, pcoor, cid, cname, cshort, ccoor, coid, coname, coshort, cocoor))

# print(len(prov_all))
# print(prov_all)
# json_dump(prov_all, 'prov_all.json')

# print(len(city_all))
# print(city_all)
# json_dump(city_all, 'city_all.json')
# for c in city_all:
#     print(c)

# json_dump(county_all, 'county_all.json')

with open('locations.txt', 'w') as f:
    for loc in locations_all:
        f.write('|'.join(loc))
        f.write('\n')

# print(len(prov_all) + len(city_all) + len(county_all))

json_dump(locations_all, 'locations_all.json')


def save(locs):
    SQL = """INSERT INTO location_all (code, name, short_name, geo, level, parent_code)
                 VALUES ('{}', '{}', '{}', '{}', '{}', '{}')"""

    import MySQLdb
    db = MySQLdb.connect('localhost', 'root', 'nadileaf', 'knowledge_db', charset='utf8', use_unicode=True)
    cur = db.cursor()

    for loc in locs:
        sql = SQL.format(loc[0], loc[1], loc[2], loc[3], loc[4], loc[5])
        print(sql)
        cur.execute(sql)

    db.commit()
