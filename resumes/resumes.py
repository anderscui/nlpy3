# coding=utf-8
import json
resumes = json.load(open('resumes.json'))

columns = ['resume_birth', 'resume_sex', 'resume_location', 'resume_self_evaluation', 'resume_language', 'resume_skill', 'resume_project_experience', 'resume_education_experience', 'resume_work_experience']

new_resumes = []
for r in resumes:
    if r['resume_location'] not in ['上海', '北京', '杭州', '苏州']:
        continue

    new_r = {}
    for c in columns:
        new_r[c] = r[c]
    new_resumes.append(new_r)

json.dump(new_resumes, open('yifeng.json', 'w'), ensure_ascii=False)
