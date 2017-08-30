# coding=utf-8
import json

import dateparser

yifeng = json.load(open('yifeng_small.json'))
print(len(yifeng))
schools = json.load(open('sch_v.json'))
schools.update(json.load(open('sch_f_v.json')))
print(len(schools))

DEGREE_NORMALIZE = {
    "高中": "高中",
    "大专": "专科",
    "专科": "专科",
    "本科": "本科",
    "学士": "本科",

    "硕士": "学术型硕士",
    "硕士研究生": "学术型硕士",
    "博士": "学术型博士",
    "博士研究生": "学术型博士",
    "博士后": "学术型博士",

    "研究生": "专业学位硕士",
    "MBA": "专业学位硕士",
    "EMBA": "专业学位硕士",

    "大学在读": "本科",
    "本科在读": "本科",
    "硕士在读": "学术型硕士",
    "博士在读": "学术型博士",

    "中专": "高中",
    "中技": "高中",
    "初中": "高中"
}


def normalize_date(d):
    if len(d) <= 5:
        return None

    parsed = dateparser.parse(d)
    return parsed.strftime('%Y/%m/%d')


def extract_edu(item):
    school = item['schoolName']
    if school in schools:
        edu = {'school': school,
               'major': item['specialty'],
               'degree': DEGREE_NORMALIZE.get(item['education'], '高中'),
               'start_date': normalize_date(item['startTime']),
               'end_date': normalize_date(item['endTime']),
               'until_now': False}
        return edu
    else:
        return None


def extract_edus(r):
    edus_str = r['resume_education_experience']
    edus = json.loads(edus_str)
    edus = [extract_edu(edu) for edu in edus]
    edus = [edu for edu in edus if edu]
    return edus


def extract_work(item):
    work = {'company': item['compName'],
            'description': item.get('workDesc', ''),
            'position': item.get('jobTitle', ''),
            'start_date': normalize_date(item['startTime']),
            'end_date': normalize_date(item['endTime']),
            'until_now': False}
    return work


def extract_works(r):
    works_str = r['resume_work_experience']
    works = json.loads(works_str)
    works = [extract_work(w) for w in works]
    works = [work for work in works if work]
    return works


def extract_proj(item):
    proj = {'name': item['projectName'],
            'description': item.get('projectDesc', '') + '\n' + item.get('responsibilityDesc', ''),
            'position': None,
            'start_date': normalize_date(item['startTime']),
            'end_date': normalize_date(item['endTime']),
            'until_now': False}
    return proj


def extract_projs(r):
    projs_str = r['resume_project_experience']
    projs = json.loads(projs_str)
    projs = [extract_proj(w) for w in projs]
    projs = [proj for proj in projs if proj]
    return projs


def extract_skills(r):
    skills_str = r['resume_skill']
    skills = json.loads(skills_str)
    return [s['skillName'] for s in skills]


if __name__ == '__main__':
    extracted = []
    for r in yifeng:
        resume = {}
        edus = extract_edus(r)
        # print(edus)
        resume['educations'] = edus

        works = extract_works(r)
        # print(works)
        resume['works'] = works

        # projs = extract_projs(r)
        # print(projs)
        skills = extract_skills(r)
        # if skills:
        #     print(skills)
        resume['skills'] = skills

        extracted.append(resume)

    print(len(extracted))
