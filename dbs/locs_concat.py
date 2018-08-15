# coding=utf-8
import json

from toolz import take


def json_load(file):
    return json.load(open(file))


def json_dump(obj, file):
    json.dump(obj, open(file, 'w'), ensure_ascii=False)


def read_lines(file):
    with open(file) as f:
        for l in f:
            yield l.strip()


locs_all = json_load('locations_all.json')
print(len(locs_all))

last_char = set()
for loc in locs_all:
    loc_id, lname, sname, _, level, pid = loc
    last_char.add(lname[-1])

# {'区', '县', '域', '岛', '州', '市', '旗', '盟', '省'}

locs_dict = {}
for loc in locs_all:
    loc_id, lname, sname, _, level, pid = loc
    locs_dict[loc_id] = {'name': lname, 'short_name': sname, 'level': level, 'parent': pid}

locs12 = []
for loc in locs_all:
    loc_id, lname, sname, _, level, pid = loc
    if level == 'city':
        cur = []
        city = locs_dict[pid]
        cur.append(city['name'] + lname)
        if city['short_name'] != city['name']:
            cur.append(city['short_name'] + lname)
        if sname != lname:
            cur.append(city['name'] + sname)
            cur.append(city['short_name'] + sname)
        # print(parent['name'] + lname, parent['short_name'] + lname, parent['name'] + sname, parent['short_name'] + sname)
        locs12.extend(cur)

locs23 = []
for loc in locs_all:
    loc_id, lname, sname, _, level, pid = loc
    if level == 'district':
        cur = []
        city = locs_dict[pid]
        cur.append(city['name'] + lname)
        if city['short_name'] != city['name']:
            cur.append(city['short_name'] + lname)
        if sname != lname:
            cur.append(city['name'] + sname)
            cur.append(city['short_name'] + sname)
        # print(parent['name'] + lname, parent['short_name'] + lname, parent['name'] + sname, parent['short_name'] + sname)
        locs23.extend(cur)

locs123 = []
for loc in locs_all:
    loc_id, lname, sname, _, level, pid = loc
    if level == 'district':
        cur = []
        city = locs_dict[pid]
        prov = locs_dict[city['parent']]
        if loc_id[:2] in {'11', '12', '31', '50'}:
            cur.append(prov['name'] + lname)
        else:
            cur.append(prov['name'] + lname)
            cur.append(prov['name'] + city['name'] + lname)
        # if parent['short_name'] != parent['name']:
        #     cur.append(parent['short_name'] + lname)
        # if sname != lname:
        #     cur.append(parent['name'] + sname)
        #     cur.append(parent['short_name'] + sname)
        # print(parent['name'] + lname, parent['short_name'] + lname, parent['name'] + sname, parent['short_name'] + sname)
        locs123.extend(cur)


locs3 = []
for loc in locs_all:
    loc_id, lname, _, _, level, pid = loc
    if level == 'district':
        locs3.append(lname)


loc_v = json_load('/Users/andersc/github/aleph/aleph/data/entity/value/loc_v.json')

concatenated = locs12 + locs23 + locs123 + locs3
concatenated = {loc: 1 for loc in concatenated}
concatenated.update(loc_v)


def starts_with_loc(locs, line):
    for i in range(2, len(line)+1):
        if line[:i] in locs:
            return True
    return False


liepin = json_load('/Users/andersc/data/cvparse/loction/liepin_locs.json')
print(len(liepin))
for loc in take(100, liepin):
    if loc not in concatenated:
        print(loc)

valid_locs = []
for loc in take(200000, liepin):
    if loc not in concatenated and starts_with_loc(concatenated, loc) and not any(
            w in loc for w in {'地址', '公司', '：', ':', '(', ')', '（', '）', '/', ',', '，', ';', '；', ' ', '\t'}):
        valid_locs.append(loc)
print(len(valid_locs))

valid_locs2 = []
for l in valid_locs[:200000]:
    if any(w in l for w in {'路', '街', '胡同', '道', '巷'}):
        valid_locs2.append(l)
print(len(valid_locs2))

json_dump(valid_locs2, 'loc_details.json')
json_dump(concatenated, 'loc_std.json')
