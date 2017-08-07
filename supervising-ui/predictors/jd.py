# coding=utf-8
import json
import os
import string
from collections import defaultdict

from scan.common.chinese import remove_whitespace, RE_HAN, RE_NON_HAN

TITLES_PATH = os.path.join(os.path.dirname(__file__), 'job_titles.json')
titles = json.load(open(TITLES_PATH))
bullets = '一二三四五六七八九十' + string.digits

mappings = {'pos': '招聘职位', 'req': '职位要求', 'resp': '职位职责',
            'car': '职业发展', 'wel': '福利待遇',
            'com': '公司信息', 'int': '面试信息'}
DEFAULT_SEC_NAME = '其它信息'


def remove_non_han(text):
    return RE_NON_HAN.sub('', text)


def numbered_title(line):
    if len(line) < 3:
        return line
    if line[0] in bullets and line[1] in '、 ：）。，．).,\xa0':
        return line[2:]
    else:
        return line


def bullet_title(line):
    if len(line) < 3:
        return line
    if line[0] in string.ascii_lowercase and line[1] in '、）)':
        return line[2:]
    else:
        return line


def kangxi(s):
    # TODO: replace more, in a better way.
    s = s.replace('⾃', '自')
    s = s.replace('⽬', '目')
    s = s.replace('⼈', '人')
    s = s.replace('⾄', '至')
    s = s.replace('⽼', '老')
    s = s.replace('⽴', '立')
    s = s.replace('老', '老')
    s = s.replace('⽐', '比')
    s = s.replace('更', '更')
    s = s.replace('⼤', '大')
    s = s.replace('了', '了')
    s = s.replace('⼯', '工')
    s = s.replace('⽹', '网')
    s = s.replace('⽇', '日')
    s = s.replace('⽂', '文')
    s = s.replace('⽀', '支')
    s = s.replace('⼰', '己')
    s = s.replace('⾼', '高')
    s = s.replace('年', '年')
    s = s.replace('⼩', '小')
    s = s.replace('⽅', '方')
    s = s.replace('⽤', '用')
    s = s.replace('⼀', '一')
    s = s.replace('北', '北')
    s = s.replace('⽣', '生')
    s = s.replace('⼼', '心')
    s = s.replace('行', '行')
    s = s.replace('⽆', '无')
    s = s.replace('⼊', '入')
    s = s.replace('⼜', '又')
    s = s.replace('⿊', '黑')
    s = s.replace('⼆', '二')
    s = s.replace('⽉', '月')
    s = s.replace('⾯', '面')
    s = s.replace('⼿', '手')
    s = s.replace('不', '不')
    s = s.replace('力', '力')
    s = s.replace('⼲', '干')
    s = s.replace('⾛', '走')
    s = s.replace('⼴', '广')
    s = s.replace('⾝', '身')
    s = s.replace('⼨', '寸')
    s = s.replace('⾔', '言')
    s = s.replace('⽔', '水')
    s = s.replace('⼝', '口')
    s = s.replace('⾷', '食')
    s = s.replace('⼥', '女')
    s = s.replace('⾊', '色')
    s = s.replace('⾜', '足')
    s = s.replace('⺟', '母')
    s = s.replace('⼠', '士')
    s = s.replace('⾦', '金')
    s = s.replace('量', '量')
    s = s.replace('理', '理')
    s = s.replace('敏', '敏')
    s = s.replace('⻚', '页')
    s = s.replace('烈', '烈')
    s = s.replace('度', '度')
    s = s.replace('⻔', '门')
    s = s.replace('金', '金')
    s = s.replace('⻓', '长')
    s = s.replace('留', '留')
    s = s.replace('⻆', '角')
    s = s.replace('⽛', '牙')
    # s = s.replace('䘾', '䘾')
    s = s.replace('㡳', '底')
    s = s.replace('什', '什')
    s = s.replace('料', '料')
    s = s.replace('⾳', '音')
    s = s.replace('オ', '才')
    s = s.replace('凉', '凉')
    s = s.replace('拓', '拓')
    s = s.replace('履', '履')
    s = s.replace('隣', '隣')
    s = s.replace('器', '器')
    s = s.replace('⾮', '非')
    s = s.replace('利', '利')
    s = s.replace('略', '略')
    s = s.replace('⻛', '风')
    return s


def normalize(s):
    s = kangxi(s)
    s = s.replace('\xa0', ' ')
    s = s.replace('—', '-')
    s = s.replace('“', '"')
    s = s.replace('”', '"')
    s = s.replace('．', '.')
    s = s.replace('★', '*')
    s = s.replace('／', '/')
    s = s.replace('→', '>')
    s = s.replace('－', '-')
    s = s.replace('＋', '+')
    s = s.replace('◆', '*')
    s = s.replace('', '*')
    s = s.replace('●', '*')
    s = s.replace('’', "'")
    s = s.replace('＝', '=')
    s = s.replace('–', '-')
    s = s.replace('▶', '>')
    s = s.replace('◀', '<')
    s = s.replace('］', ']')
    s = s.replace('［', '[')
    s = s.replace('☆', '*')
    s = s.replace('☞', '>')
    s = s.replace('＊', '*')
    s = s.replace('―', '-')
    s = s.replace('｡', '。')
    s = s.replace('＃', '#')
    s = s.replace('・', '·')
    s = s.replace('〖', '[')
    s = s.replace('〗', ']')
    s = s.replace('【', '[')
    s = s.replace('】', ']')
    s = s.replace('☑', ' ')
    #
    s = s.replace('㈠', '(1)')
    s = s.replace('㈡', '(2)')
    s = s.replace('㈢', '(3)')
    s = s.replace('㈣', '(4)')
    s = s.replace('㈤', '(5)')
    s = s.replace('㈥', '(6)')
    s = s.replace('㈦', '(7)')
    s = s.replace('㈧', '(8)')
    s = s.replace('㈨', '(9)')

    s = s.replace('⑴', '(1)')
    s = s.replace('⑵', '(2)')
    s = s.replace('⑶', '(3)')
    s = s.replace('⑷', '(4)')
    s = s.replace('⑸', '(5)')
    s = s.replace('⑹', '(6)')
    s = s.replace('⑺', '(7)')
    s = s.replace('⑻', '(8)')
    s = s.replace('⑼', '(9)')

    s = s.replace('①', '(1)')
    s = s.replace('②', '(2)')
    s = s.replace('③', '(3)')
    s = s.replace('④', '(4)')
    s = s.replace('⑤', '(5)')
    s = s.replace('⑥', '(6)')
    s = s.replace('⑦', '(7)')
    s = s.replace('⑧', '(8)')
    s = s.replace('⑨', '(9)')

    s = s.replace('⒈', '1.')
    s = s.replace('⒉', '2.')
    s = s.replace('⒊', '3.')
    s = s.replace('⒋', '4.')
    s = s.replace('⒌', '5.')
    s = s.replace('⒍', '6.')
    s = s.replace('⒎', '7.')
    s = s.replace('⒏', '8.')
    s = s.replace('⒐', '9.')

    s = s.replace('１', '1.')
    s = s.replace('２', '2.')
    s = s.replace('３', '3.')
    s = s.replace('４', '4.')
    s = s.replace('５', '5.')
    s = s.replace('６', '6.')
    s = s.replace('７', '7.')
    s = s.replace('８', '8.')
    s = s.replace('９', '9.')

    s = s.replace('>', '>')
    return s


def prepro_title(line):
    line = normalize(line)
    line = line.strip()
    if not line:
        return line
    line = line.lower()
    if line[0] in '"(（':
        line = line[1:]

    line = numbered_title(line)
    line = bullet_title(line)
    line = remove_whitespace(line)
    line = remove_non_han(line)

    return line


def segment_desc(title_dict, lines):
    tags = {}
    section = 'resp'
    for i, line in enumerate(lines):
        preprocessed = prepro_title(line)
        if preprocessed in title_dict:
            section = title_dict[preprocessed]

        tags[i] = section
    return tags


def section_of_line(lines, lino):
    section = 'resp'
    for i, line in enumerate(lines):
        preprocessed = prepro_title(line)
        if preprocessed in titles:
            section = titles[preprocessed]

        if i == lino:
            break
    return section


def sec_name(sec):
    return mappings.get(sec, DEFAULT_SEC_NAME)


if __name__ == '__main__':
    s = """岗位职责
    
1.负责Java BS 或 Server端软件项目的评估及细化设计
2.能独立处理和解决项目中出现的技术问题；
3.根据开发进度和任务分配，完成相应模块软件的设计、开发、编程任务；
4.进行程序单元、功能的测试，查出软件存在的缺陷并保证开发质量； 
5.进行编制项目文档和质量记录的工作；
6.维护软件使之保持可用性和稳定性；
7.引导客户需求。

任职资格

1.有较强的沟通能力; 
2.熟悉数据库MySQL/Oracle/SQL Server中任意两类数据库；
3.可使用Eclipse、MyEclipse等开发进行高效工作；        
"""
    lines = s.splitlines()
    # titles = json.load(open('job_titles.json'))
    # segs = segment_desc(lines)
    # print(segs)
    # sec = section_of_line(lines, 2)
    # print(sec)
    # sec = section_of_line(lines, 12)
    # print(sec)

    print(set(titles.values()))
