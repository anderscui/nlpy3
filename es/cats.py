# coding=utf-8

from datetime import datetime
import json

from elasticsearch import Elasticsearch
from elasticsearch.client.cat import CatClient
from elasticsearch_dsl import Search
from elasticsearch.helpers import bulk

from es.analyzers import similar_candidates, similar_jobs, similarity

client = Elasticsearch('54.223.238.68:9200')
cat_client = CatClient(client)


class Types(object):
    job = 'job'
    candidate = 'candidate'
    job_candidate = 'job_candidate'


def now_as_string():
    # TODO: find a better solution.
    return datetime.utcnow().isoformat() + 'Z'


def get_indices():
    result = cat_client.indices(format='json')
    result = [ind['index'] for ind in result if ind['index'].startswith('can_')]
    return result


def get_all_jobs(index, estype=Types.job,
                 fields=['id'],
                 status=1, at_most=10000):
    s = Search(using=client)
    s = s.filter('term', _index=index)
    s = s.filter('term', _type=estype)
    s = s.filter('term', status=status)

    s = s.source(include=fields)
    s = s[:at_most]
    resp = s.execute()
    # print(resp.took)
    # print(resp.hits.total)
    return [hit['id'] for hit in resp]


def get_all_cans(index, estype=Types.candidate,
                 fields=['id'],
                 status=1, at_most=10000):
    s = Search(using=client)
    s = s.filter('term', _index=index)
    s = s.filter('term', _type=estype)
    s = s.filter('term', status=status)

    s = s.source(include=fields)
    s = s[:at_most]
    resp = s.execute()
    # print(resp.took)
    # print(resp.hits.total)
    return [hit['id'] for hit in resp]


def get_all_job_cans(index, estype=Types.job_candidate,
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
    # print(resp.took)
    # print(resp.hits.total)
    return [{'id': hit['id'],
             'job_id': hit['job'],
             'can_id': hit['candidate']} for hit in resp]


def calc_job(index, job_id, status):
    print('calculate similar candidates for job({})'.format(job_id))
    req = {'index': index, 'job_id': job_id, 'status': status}
    analyzed = similar_candidates(req)
    print('found {} candidates'.format(len(analyzed)))
    return analyzed


def calc_can(index, can_id, status=1):
    req = {'index': index, 'can_id': can_id, 'status': status}
    analyzed = similar_jobs(req)
    return analyzed


def calc_job_can(index, job_id, can_id):
    print('calculate similarity between job({}) and candidate({})'.format(job_id, can_id))
    req = {'index': index, 'job_id': job_id, 'can_id': can_id}
    analyzed = similarity(req)
    return analyzed


def sync_index(index):
    print('start to sync index: {}'.format(index))
    start = datetime.now()

    cans = get_all_cans(index, status=0)
    print('found {} cans'.format(len(cans)))
    # cans = [22, 14]
    sync_cans(index, cans, status=1)

    jobs = get_all_jobs(index, status=1)
    print('found {} jobs'.format(len(jobs)))
    sync_jobs(index, jobs, status=0)

    job_cans = get_all_job_cans(index)
    print('found {} job_cans'.format(len(job_cans)))
    invalid = [jc for jc in job_cans if jc['job_id'] not in jobs or jc['can_id'] not in cans]
    print('invalid job_cans: {}'.format(invalid))
    job_cans = [jc for jc in job_cans if jc['job_id'] in jobs and jc['can_id'] in cans]
    print('job_cans after filtering: {}'.format(len(job_cans)))
    sync_job_cans(index, job_cans)

    print(datetime.now() - start)


def sync_cans(index, can_ids, status=1):
    start = datetime.now()
    print('sync cans of index({}):'.format(index))
    print(can_ids)

    actions = []
    now = now_as_string()
    for can_id in can_ids:
        analyzed = calc_can(index, can_id, status)
        print(analyzed)
        sim_jobs = []
        for item in analyzed:
            sim_job = {'job_id': item['job_id'],
                       'radar': json.dumps(item['can_radar'], ensure_ascii=False),
                       'salary': item['can_salary'],
                       'similarity': item['similarity'],
                       'createdAt': now}
            sim_jobs.append(sim_job)
        action = {'doc': {'jobs': sim_jobs},
                  '_op_type': 'update',
                  '_index': index,
                  '_type': Types.candidate,
                  '_id': can_id}
        actions.append(action)

    bulk(client,
         actions,
         chunk_size=500,
         timeout='60s')

    print(datetime.now() - start)


def sync_jobs(index, job_ids, status=1):
    start = datetime.now()

    print('sync jobs of index({}):'.format(index))
    print(job_ids)

    actions = []
    now = now_as_string()
    for job_id in job_ids:
        analyzed = calc_job(index, job_id, status)
        sim_cans = []
        for item in analyzed:
            sim_can = {'can_id': item['can_id'],
                       'radar': json.dumps(item['can_radar'], ensure_ascii=False),
                       'salary': item['can_salary'],
                       'similarity': item['similarity'],
                       'createdAt': now}
            sim_cans.append(sim_can)
        action = {'doc': {'cans': sim_cans},
                  '_op_type': 'update',
                  '_index': index,
                  '_type': Types.job,
                  '_id': job_id}
        actions.append(action)

    bulk(client,
         actions,
         chunk_size=500,
         timeout='60s')

    print(datetime.now() - start)


def sync_job_cans(index, job_cans):
    start = datetime.now()

    print('sync job_cans:')
    print(job_cans)

    result = []
    now = now_as_string()
    for job_can in job_cans:
        analyzed = calc_job_can(index, job_can['job_id'], job_can['can_id'])
        sim = {}
        if analyzed:
            sim = {'radar': json.dumps(analyzed['can_radar'], ensure_ascii=False),
                   'salary': analyzed['can_salary'],
                   'similarity': analyzed['similarity'],
                   'createdAt': now}
        data = {'doc': {'sim': sim},
                '_op_type': 'update',
                '_index': index,
                '_type': Types.job_candidate,
                '_id': job_can['id']}
        result.append(data)

    bulk(client,
         result,
         chunk_size=500,
         timeout='60s')

    print(datetime.now() - start)


if __name__ == '__main__':

    start = datetime.now()

    indices = get_indices()
    for index in indices:
        # print(index)
        # index = 'can_tenant_mesoortest'
        sync_index(index)

    print(datetime.now() - start)

    # print(calc_job(index, 14, 0))
    # print(calc_can(index, 22, 1))
    # print(calc_job_can(index, 11, 22))
