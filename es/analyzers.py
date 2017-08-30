# coding=utf-8
import json
import requests

from datetime import datetime

ANALYSIS_SERVER = 'http://54.223.238.68:8000'

SIMILAR_CANDIDATES_API = ANALYSIS_SERVER + '/v1/candidates?page=1&size=200'
SIMILAR_JOBS_API = ANALYSIS_SERVER + '/v1/jobs?page=1&size=200'
SIMILARITY_API = ANALYSIS_SERVER + '/v1/analysis/similarity'


def post_api(url, data):
    headers = {'content-type': 'application/json'}
    try:
        start = datetime.now()
        response = requests.post(url, data=json.dumps(data), headers=headers)
        print(datetime.now() - start)
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            print('api error: ')
            print(url, data)
            return None
    except:
        print('api error: ')
        print(url, data)
        return None


def similar_candidates(job_data):
    print('getting similar candidates')
    print(job_data)
    result = post_api(SIMILAR_CANDIDATES_API, job_data)
    return result if result else []


def similar_jobs(candidate_data):
    print('getting similar jobs')
    print(candidate_data)
    result = post_api(SIMILAR_JOBS_API, candidate_data)
    return result if result else []


def similarity(sim_data):
    print('getting similarity')
    print(sim_data)
    result = post_api(SIMILARITY_API, sim_data)
    return result if result else {}


if __name__ == '__main__':
    can = {'index': 'can_tenant_mesoortest', 'job_id': 14, 'status': 0}
    analyzed = similar_candidates(can)
    print(analyzed)
