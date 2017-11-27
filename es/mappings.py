# coding=utf-8
import json

from collections import defaultdict
from elasticsearch import Elasticsearch
from elasticsearch.client import CatClient, IndicesClient

client = Elasticsearch('52.80.17.209:9200')
cat_client = CatClient(client)
ind_client = IndicesClient(client)


def get_indices():
    result = cat_client.indices(format='json')
    result = [ind['index'] for ind in result if ind['index'].startswith('can_')]
    return result


def get_mappings(index, estype=None):
    print('index: ', (index, estype))
    maps = ind_client.get_mapping(index, estype, format='json')

    if index not in maps:
        print('index not found')
        return

    fields = maps[index]['mappings'][estype]['properties']
    # if 'require' in props:
    #     print(json.dumps(props['require'], indent=2))
    return fields


def get_requires():
    requires = defaultdict(list)
    for index in get_indices():
        fields = get_mappings(index, 'job')
        if fields:
            req = json.dumps(fields.get('require', ''), indent=2)
            requires[req].append(index)

    for req, indices in requires.items():
        print(req, indices)


def get_type_fields(estype='job'):
    result = defaultdict(list)
    for index in get_indices():
        fields = get_mappings(index, estype)
        if fields:
            for field in fields:
                result[field].append(index)

    return result


def get_resume_fields():
    result = defaultdict(list)
    for index in get_indices():
        fields = get_mappings(index, 'candidate')
        if fields and 'resume' in fields:
            # print(fields['resume'])
            for field in fields['resume']['properties']:
                result[field].append(index)

    return result


if __name__ == '__main__':
    # get_mappings('can_ocean', 'job')
    # fields = get_type_fields('job')
    # fields = get_type_fields('candidate')
    # for k, v in fields.items():
    #     print(k, v)

    fields = get_resume_fields()
    for k, v in fields.items():
        print(k, v)
