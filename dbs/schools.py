# coding=utf-8
import requests
from bs4 import BeautifulSoup


def extract_school_details(table_id='全列表', tag='普通高等学校'):
    header = soup.find(id=table_id)
    sch_table = header.parent.find_next_sibling('table')
    rows = list(sch_table.find_all('tr'))

    school_head = [c.string for c in rows[0].find_all('th')[1:5]]
    schools = []
    for row in rows[1:]:
        texts = [c.string for c in row.find_all('td')[1:5]]
        schools.append({h: t for h, t in zip(school_head, texts)})
        for s in schools:
            s['tag'] = tag
    return schools


url = 'https://zh.wikipedia.org/zh-cn/中国大陆高等学校列表'
r = requests.get(url)
print(r)
soup = BeautifulSoup(r.content, 'html.parser')


if __name__ == '__main__':
    normals = extract_school_details('全列表', '普通高等学校')
    print(len(normals))

    jfj = extract_school_details('解放军院校', tag='解放军院校')
    print(len(jfj))

    wujing = extract_school_details('武警部队院校', tag='武警部队院校')
    print(len(wujing))

    chengren = extract_school_details('成人高等学校', tag='成人高等学校')
    print(len(chengren))

    school_names = []
    school_names.extend([s['学校名称'] for s in normals])
    school_names.extend([s['学校名称'] for s in chengren])
    school_names.extend([s['院校名称'] for s in jfj])
    school_names.extend([s['院校名称'] for s in wujing])
    print(len(school_names))
