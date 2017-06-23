# coding=utf-8

import datetime

from elasticsearch import Elasticsearch
from elasticsearch.client.cat import CatClient
from elasticsearch_dsl import Search

client = Elasticsearch('54.223.238.68:9200')
cat_client = CatClient(client)
types = ['job', 'candidate', 'job_candidate']


def get_indices():
    result = cat_client.indices(format='json')
    result = [ind['index'] for ind in result if ind['index'].startswith('can_')]
    return result


def get_all_jobs(index, estype='job',
                 fields=['id'],
                 status=1, at_most=10000):
    s = Search(using=client)
    s = s.filter('term', _index=index)
    s = s.filter('term', _type=estype)
    s = s.filter('term', status=status)

    s = s.source(include=fields)
    s = s[:at_most]
    resp = s.execute()
    print(resp.took)
    print(resp.hits.total)
    return [hit['id'] for hit in resp]


def get_all_cans(index, estype='candidate',
                 fields=['id'],
                 status=1, at_most=10000):
    s = Search(using=client)
    s = s.filter('term', _index=index)
    s = s.filter('term', _type=estype)
    s = s.filter('term', status=status)

    s = s.source(include=fields)
    s = s[:at_most]
    resp = s.execute()
    print(resp.took)
    print(resp.hits.total)
    return [hit['id'] for hit in resp]


def get_all_job_cans(index, estype='job_candidate',
                     fields=['id', 'job', 'candidate'],
                     status=None, at_most=10000):
    s = Search(using=client)
    s = s.filter('term', _index=index)
    s = s.filter('term', _type=estype)
    if status:
        s = s.filter('term', status=status)

    s = s.source(include=fields)
    s = s[:at_most]
    resp = s.execute()
    print(resp.took)
    print(resp.hits.total)
    return [{'id': hit['id'],
             'job_id': hit['job'],
             'can_id': hit['candidate']} for hit in resp]


def sync_index(index):
    cans = get_all_cans(index, status=0)
    print('found {} cans'.format(len(cans)))
    jobs = get_all_jobs(index, status=1)
    print('found {} jobs'.format(len(jobs)))
    job_cans = get_all_job_cans(index)
    print('found {} job_cans'.format(len(job_cans)))


if __name__ == '__main__':
    # indices = get_indices()
    # for i in indices:
    #     print(i)
    index = 'can_tenant_mesoortest'
    sync_index(index)
