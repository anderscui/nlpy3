# coding=utf-8

import datetime

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

client = Elasticsearch('54.223.238.68:9200')


def search_jobs():
    s = Search(using=client)
    s = s.filter('term', _index='can_tenant_chouun')
    s = s.filter('term', _type='job')
    s = s.filter('term', id=12)

    resp = s.execute()
    for hit in resp:
        analysis = hit['analysis']
        print(type(analysis))
        print(dir(analysis))


def search_cans():
    work_years = 0
    salary_low = 1000
    salary_high = 50000
    status = 0
    job_3l_nums = [
        "13040342",
        "02250254",
        "02250166",
        "04550449",
        "00510085"
      ]

    s = Search(using=client, index='can_tenant_chouun')

    # s = s.filter('term', _index='can_tenant_chouun')
    s = s.filter('term', _type='candidate')

    q = Q('nested', path='analysis',
          query=Q('term', **{'analysis.job_3l_num': job_3l_nums[0]}))
    for job_3l_num in job_3l_nums[1:]:
        q |= Q('nested', path='analysis',
               query=Q('term', **{'analysis.job_3l_num': job_3l_num}))
    # s = s.filter('term', status=status)
    s = s.query(q)
    s = s.query(Q('nested', path='analysis',
                  query=Q('range', **{'analysis.salary': {'gte': int(salary_low) - 3000}})))
    s = s.filter('range', years={
        'lte': datetime.date.today().year - int(work_years)
    })

    s = s.source(include=['id', 'analysis'])
    s = s[0:200]

    resp = s.execute()
    print(resp['took'])
    print(resp['hits']['total'])
    # for hit in resp:
    #     analysis = hit['analysis']
    #     print(type(analysis))
    #     print(dir(analysis))


if __name__ == '__main__':
    start = datetime.datetime.now()
    search_cans()
    print(datetime.datetime.now() - start)
