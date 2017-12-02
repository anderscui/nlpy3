# coding=utf-8
import json

from collections import defaultdict
from elasticsearch import Elasticsearch
from elasticsearch.client import CatClient, IndicesClient, NodesClient

# client = Elasticsearch('54.222.177.58:9200')
client = Elasticsearch('54.223.226.77:9200')
cat_client = CatClient(client)
ind_client = IndicesClient(client)
node_client = NodesClient(client)


def get_indices():
    result = cat_client.indices(format='json')
    result = [ind['index'] for ind in result if ind['index'].startswith('can_')]
    # result = [ind['index'] for ind in result if ind['index']]
    return result


def get_indices_from_db():
    indices = []
    with open('indices.txt') as f:
        for l in f:
            indices.append(l.strip())
    return indices


def create_index_with_alias(index):
    if ind_client.exists(index):
        ind_client.delete(index)

    ind_client.create(index)

    if index.startswith('can_'):
        alias = index[4:]
        ind_client.put_alias(index, alias)


def put_mapping(index, estype, mapping_file):
    print('doc type: {}/{}'.format(index, estype))

    with open(mapping_file) as f:
        mapping = f.read()

    resp = ind_client.put_mapping(estype, mapping, index=index)
    print(resp)
    return resp


def init_index(index):
    print('start to init index: ', index)
    create_index_with_alias(index)
    put_mapping(index, 'job', 'job.json')
    put_mapping(index, 'candidate', 'candidate.json')
    put_mapping(index, 'job_candidate', 'job_candidate.json')


def get_nodes():
    print(node_client.info())


if __name__ == '__main__':
    # indices = get_indices()
    # json.dump(indices, open('indices.json', 'w'), ensure_ascii=False)

    indices = get_indices_from_db()
    # indices = ['can_ocean', 'can_tenant_neitui', 'can_tenant_jobs']
    indices = ['can_tenant_junxianandpinpin', 'can_tenant_chiyu_computer_tech', 'can_tenant_chouun',
               'can_tenant_jingdong_nettech', 'can_tenant_meiruo']
    for index in indices:
        init_index(index)

    # get_nodes()
