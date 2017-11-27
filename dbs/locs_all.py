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


prov_full = json_load('provinces_full.json')
city_full = json_load('cities_full.json')

locs_all = json_load('locations_all.json')
cn = locs_all['districts'][0]
print(cn.keys())
provs = cn['districts']

prov_all = []
city_all = []
county_all = []
locations_all = []
for p in provs:
    pid = p['adcode']
    pname = p['name']
    p_short_id = pid[:2]
    pshort = prov_full[p_short_id][1]
    pcoor = change_geo(p['center'])
    prov_all.append((pid, pname, pshort, pcoor))

    cities = p['districts']
    for c in cities:
        cid = c['adcode']
        cname = c['name']
        cshort = None
        c_short_id = cid[:4]
        if c_short_id in city_full:
            cshort = city_full[c_short_id][1]
        else:
            print(cid, cname)
        ccoor = change_geo(c['center'])
        city_all.append((cid, cname, cshort, ccoor))

        counties = c['districts']
        for co in counties:
            coid = co['adcode']
            coname = co['name']
            coshort = None
            cocoor = change_geo(co['center'])
            county_all.append((coid, coname, coshort, cocoor))
            locations_all.append((pid, pname, pshort, pcoor, cid, cname, cshort, ccoor, coid, coname, coshort, cocoor))

# print(len(prov_all))
# print(prov_all)
json_dump(prov_all, 'prov_all.json')

# print(len(city_all))
# print(city_all)
json_dump(city_all, 'city_all.json')
for c in city_all:
    print(c)

# for c in locations_all:
#     print(c)

json_dump(county_all, 'county_all.json')
