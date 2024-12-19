#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from math import *
import numpy as np

from wikidata_filter.landinn.util import get_conn


def linear_normalization(dict_tech_id_to_emerging_degree):
    limit_lower = 10.0
    limit_upper = 90.0
    value_min = np.array(np.array(list(dict_tech_id_to_emerging_degree.values()))).min()
    value_max = np.array(np.array(list(dict_tech_id_to_emerging_degree.values()))).max()

    k = float(limit_upper-limit_lower + 1)/float(value_max-value_min + 1)
    b = float(limit_lower*value_max-limit_upper*value_min + 1)/float(value_max-value_min + 1)

    for tech_id in dict_tech_id_to_emerging_degree:
        if dict_tech_id_to_emerging_degree[tech_id] == 0:
            continue
        else:
            dict_tech_id_to_emerging_degree[tech_id] = round(k*float(dict_tech_id_to_emerging_degree[tech_id]) + b, 2)
    return dict_tech_id_to_emerging_degree


# 第二步函数
def get_doc_count(list_tech_id, list_time_slot):
    dict_tech_id_to_doc_count = {}
    sql = '''
    SELECT tech_id, `year`, count 
    FROM word_frequency_search_results_es_20241023
    WHERE source = 'paper' AND tech_id IN %s AND `year` IN %s
    '''

    with get_conn() as connect:
        with connect.cursor() as cursor:
            cursor.execute(sql, (list_tech_id, list_time_slot))
            connect.commit()
            list_results = list(cursor.fetchall())

    for i in list_results:
        tech_id = int(i[0])
        year = int(i[1])
        count = int(i[2])
        if tech_id not in dict_tech_id_to_doc_count:
            dict_tech_id_to_doc_count[tech_id] = [0]*len(list_time_slot)
        dict_tech_id_to_doc_count[tech_id][year-list_time_slot[0]] = count

    return dict_tech_id_to_doc_count


def cal_critic(dict_tech_id_to_novelty_and_growth):
    list_data = []
    for tech_id in dict_tech_id_to_novelty_and_growth:
        list_data.append(dict_tech_id_to_novelty_and_growth[tech_id])

    data_1 = np.array(list_data)
    data_2 = data_1.copy()
    [m, n] = data_2.shape
    index_all = np.arange(n)
    # index = np.delete(index_all, index)
    index = index_all
    for j in index:
        d_max = max(data_1[:, j])
        d_min = min(data_1[:, j])
        data_2[:, j] = (data_1[:, j]-d_min+0.1)/(d_max-d_min+0.1)

    #对比性
    the = np.std(data_2, axis=0)
    # data_3 = data_2.copy()
    #矛盾性
    data_3 = list(map(list, zip(*data_2))) #矩阵转置
    r = np.corrcoef(data_3)   #求皮尔逊相关系数
    f = np.sum(1-r, axis=1)
    #信息承载量
    c = the*f
    w = list(c/sum(c))  #计算权重
    s = np.dot(data_2, w)
    list_score = list(100*s/max(s)) #计算得分

    # weights = [0.20480263, 0.1875107, 0.4188841, 0.18880257]

    # print('权重:', weights)
    dict_tech_id_to_emerging_degree = {}
    list_id = list(dict_tech_id_to_novelty_and_growth.keys())
    for i in range(len(list_id)):
        id = list_id[i]
        score = list_score[i]
        dict_tech_id_to_emerging_degree[id] = round(log(score + 0.1)*10.0, 2)

    list_score = list(dict_tech_id_to_emerging_degree.values())
    if min(list_score) < 0:
        bias = abs(min(list_score))
        for k in dict_tech_id_to_emerging_degree:
            dict_tech_id_to_emerging_degree[k] = round(dict_tech_id_to_emerging_degree[k] + bias, 2)

    for k in dict_tech_id_to_emerging_degree:
        dict_tech_id_to_emerging_degree[k] = round(dict_tech_id_to_emerging_degree[k]*2, 2)

    return dict_tech_id_to_emerging_degree


# 第三步函数
def calculate_emerging_degree(list_time_slot, dict_tech_id_to_doc_count):
    list_doc_count_all = [dict_tech_id_to_doc_count[i] for i in dict_tech_id_to_doc_count]
    dict_tech_id_to_novelty_and_growth_and_hot = {}
    dict_index_to_doc_count_all = {}
    for i in range(len(list_time_slot)):
        dict_index_to_doc_count_all[i] = np.array(list_doc_count_all)[:, i].tolist()
    for tech_id in dict_tech_id_to_doc_count:
        list_doc_count = dict_tech_id_to_doc_count[tech_id]

        if sum(list_doc_count) == 0:
            dict_tech_id_to_novelty_and_growth_and_hot[tech_id] = [0.0, 0.0, 0.0]
            continue

        # 新颖性>5
        novelty = 0.0
        for index in range(len(list_doc_count)):
            temp = float(index + 1)*float(list_doc_count[index])/float(sum(list_doc_count))
            novelty += temp

        # 增长性>0
        growth = 0.0
        for index in range(1, len(list_doc_count)):
            temp = (float(float(list_doc_count[index]) - float(list_doc_count[index - 1])) + 1)/(float(list_doc_count[index - 1]) + 1)
            growth += temp
        growth = float(growth)/9.0

        # 热点性>0
        hot = 0.0
        for index in range(len(list_doc_count)):
            _sum = float(sum(dict_index_to_doc_count_all[index]))
            if _sum == 0:
                continue
            temp = float(index + 1)*float(list_doc_count[index])/_sum*float(np.mean(dict_index_to_doc_count_all[index]))
            hot += temp

        if novelty > 5 and growth > 0:
            dict_tech_id_to_novelty_and_growth_and_hot[tech_id] = [novelty, growth, hot]
        else:
            dict_tech_id_to_novelty_and_growth_and_hot[tech_id] = [0.0, 0.0, 0.0]
    # CRITIC
    dict_tech_id_to_emerging_degree = cal_critic(dict_tech_id_to_novelty_and_growth_and_hot)

    dict_tech_id_to_emerging_degree = linear_normalization(dict_tech_id_to_emerging_degree)

    return dict_tech_id_to_emerging_degree


def emerging_degree(list_tech_id, years_span=10):
    year_end = datetime.date.today().year
    list_time_slot = [year for year in range(year_end - years_span + 1, year_end + 1)]

    # 第二步：获取技术词语的词频
    # {"技术词语1": [1, 2, 3, 5, 2, 6, 3...], "技术词语2": [1, 2, 3, 5, 2, 6, 3...], ...}
    dict_tech_id_to_doc_count = get_doc_count(list_tech_id, list_time_slot)

    # 第三步：计算技术词语的新兴度
    dict_tech_id_to_emerging_degree = calculate_emerging_degree(list_time_slot, dict_tech_id_to_doc_count)
    # {"技术词语id1":[year, active_trend, recent_trend, slope, emerging_degree], "技术词语id2":[year, active_trend, recent_trend, slope, emerging_degree], ...}

    return dict_tech_id_to_emerging_degree, list_time_slot


def calc(rows: list, target_key: str, *args, **kwargs):
    tech_ids = [row['golaxy_vocab_id'] for row in rows]
    res, years = emerging_degree(tech_ids)
    for row in rows:
        tech_id = row['golaxy_vocab_id']
        row['year'] = years[-1]
        row[target_key] = res[tech_id]

    return rows
