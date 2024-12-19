#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import copy
import numpy as np
from math import *

from wikidata_filter.landinn.util import get_conn


class HotDegreeComputingEngine:
    def __init__(self, duration=2):
        # self.kwtree = KeywordTree(case_insensitive=True)
        self.duration = duration

    def compute_word_info(self, words, dict_tec_name_to_doc_count_per_year):
        """
        为每个词计算历史词频、当前词频、总词频(历史词频+当前词频)、总词频率(当前词频/总词频)
        :param words: 词列表
        :param dict_tec_name_to_doc_count_per_year: 所有时间节点上的词频，格式为：
        {"技术词语1":[1,2,3,5,2,6,3...], "技术词语2":[1,2,3,5,2,6,3...], ...}

        :return: word_rate_map: Dict: 每个词的历史词频和当前词频,
                 compute_res_for_each_word: Dict: 每个词的总词频和总词频率
                 num_count_avg: Float： 所有词总词频均值: (W1(总词频) + W2(总词频) +...+WN(总词频)) / N
                 rate_count_avg: Flaot: 所有词总词频率均值: (W1(总词频率) + W2(总词频率) +...+WN(总词频率)) / N
        """

        word_rate_map = dict()
        for w in words:
            if w in dict_tec_name_to_doc_count_per_year:
                if dict_tec_name_to_doc_count_per_year[w][0] == 0 and dict_tec_name_to_doc_count_per_year[w][1] == 0:
                    word_rate_map[w] = {
                        'history_num': 1,
                        'current_num': 1
                    }
                else:
                    word_rate_map[w] = {
                        'history_num': dict_tec_name_to_doc_count_per_year[w][0],
                        'current_num': dict_tec_name_to_doc_count_per_year[w][1]
                    }
            else:
                word_rate_map[w] = {
                    'history_num': 1,
                    'current_num': 1
                }

        compute_res_for_each_word = dict()
        num_count = 0
        rate_count = 0
        for w, tp in word_rate_map.items():
            if not w in compute_res_for_each_word:
                compute_res_for_each_word[w] = dict()
                compute_res_for_each_word[w]['sum'] = tp['history_num'] + tp['current_num']
                compute_res_for_each_word[w]['rate'] = tp['current_num'] / compute_res_for_each_word[w]['sum']
            num_count += compute_res_for_each_word[w]['sum']
            rate_count += compute_res_for_each_word[w]['rate']
        num_count_avg = num_count / (len(words) + 1)
        rate_count_avg = rate_count / (len(words) + 1)
        return (word_rate_map, compute_res_for_each_word, num_count_avg, rate_count_avg)

    def compute_word_info_newton(self, words, dict_tec_name_to_doc_count_per_year):
        """
        为每个词计算历史词频、当前词频、总词频(历史词频+当前词频)、总词频率(当前词频/总词频)
        :param words: 词列表
        :param dict_tec_name_to_doc_count_per_year: 所有时间节点上的词频，格式为：
        {"技术词语1":[1,2,3,5,2,6,3...], "技术词语2":[1,2,3,5,2,6,3...], ...}
        :return: word_rate_map: Dict: 每个词的历史词频和当前词频
        """
        word_rate_map = dict()
        for w in words:
            if w in dict_tec_name_to_doc_count_per_year:
                if dict_tec_name_to_doc_count_per_year[w][0] == 0 and dict_tec_name_to_doc_count_per_year[w][1] == 0:
                    word_rate_map[w] = {
                        'history_num': 1,
                        'current_num': 1
                    }
                else:
                    word_rate_map[w] = {
                        'history_num': dict_tec_name_to_doc_count_per_year[w][0],
                        'current_num': dict_tec_name_to_doc_count_per_year[w][1]
                    }
            else:
                word_rate_map[w] = {
                    'history_num': 1,
                    'current_num': 1
                }

        return word_rate_map

    def bayes_func(self, cur_sum, cur_rate, num_avg, rate_avg):
        """
        贝叶斯均值计算
        :param cur_sum: 当前总词频
        :param cur_rate: 当前总词频率
        :param num_avg: 所有词总词频均值
        :param rate_avg: 所有词总词频率均值
        :return:
        """
        return (cur_sum * cur_rate + num_avg * rate_avg) / (cur_sum + num_avg + 1)

    def newton_func(self, cur_num, his_num, time_diff):
        """
        牛顿冷却系数计算
        :param cur_num: int: 当前词频
        :param his_num: int: 历史词频
        :param time_diff: int: 时间差
        :return:
        """
        return float(log(float(cur_num+1)/float(his_num+1), e))/float(time_diff)

    def bn_hot(self, dict_tech_id_to_doc_count_split, flag='newton'):
        """
        词热度值计算: Hot = 0.7 * bayes_func + 0.3 * newton_func
        :param words: 词列表
        :param history_text: 历史文本
        :param dict_tec_name_to_doc_count_per_year: 所有时间节点上的词频，格式为：
        {"技术词语1":[1,2,3,5,2,6,3...], "技术词语2":[1,2,3,5,2,6,3...], ...}

        :return: Dict: {
            word: hot_value
        }
        已按热度值降序排序
        """
        # # fixme test ###################
        words = list(dict_tech_id_to_doc_count_split.keys())
        if flag == 'newton':
            bn_word_hot_map = dict()
            word_rate_map = self.compute_word_info_newton(words, dict_tech_id_to_doc_count_split)
            for word in words:
                newton = self.newton_func(word_rate_map[word]['current_num'],
                                          word_rate_map[word]['history_num'], self.duration - 1)
                bn_word_hot_map[word] = newton
                # bn_word_hot_map[word] = 0.2 * bayes + 0.8 * newton
            # sortDict = sorted(bn_word_hot_map.items(), key=lambda x: x[1], reverse=True)
            # return OrderedDict(sortDict)
            return bn_word_hot_map
        else:
            bn_word_hot_map = dict()
            word_rate_map, compute_res_for_each_word, num_count_avg, rate_count_avg = self.compute_word_info(words,
                                                                                                             dict_tech_id_to_doc_count_split)
            for word in words:
                bayes = self.bayes_func(compute_res_for_each_word[word]['sum'],
                                        compute_res_for_each_word[word]['rate'],
                                        num_count_avg,
                                        rate_count_avg)

                newton = self.newton_func(word_rate_map[word]['current_num'],
                                 word_rate_map[word]['history_num'], self.duration - 1)

                # bn_word_hot_map[word] = bayes
                # bn_word_hot_map[word] = newton
                bn_word_hot_map[word] = 0.2 * bayes + 0.8 * newton
            # sortDict = sorted(bn_word_hot_map.items(), key=lambda x: x[1], reverse=True)
            # return OrderedDict(sortDict)
            return bn_word_hot_map


def linear_normalization(dict_tech_id_to_hot_degree):
    limit_lower = 10.0
    limit_upper = 90.0
    value_min = np.array(np.array(list(dict_tech_id_to_hot_degree.values()))).min()
    value_max = np.array(np.array(list(dict_tech_id_to_hot_degree.values()))).max()

    k = float(limit_upper-limit_lower+1)/float(value_max-value_min+1)
    b = float(limit_lower*value_max-limit_upper*value_min+1)/float(value_max-value_min+1)

    for tech_id, hot_degree in dict_tech_id_to_hot_degree.items():
        for n in range(len(hot_degree)):
            if hot_degree[n] == 0:
                continue
            else:
                hot_degree[n] = round(k*float(hot_degree[n]) + b, 2)
        dict_tech_id_to_hot_degree[tech_id] = hot_degree

    return dict_tech_id_to_hot_degree


# 第2步函数
def get_doc_count(list_tech_id, list_time_slot):
    # es
    list_tech_id_to_doc_count_all_es = []
    connect = get_conn()
    for source in ['paper', 'patent', 'news', 'project']:
        dict_tech_id_to_doc_count = {}
        sql = '''
            SELECT tech_id, `year`, count 
            FROM word_frequency_search_results_es_20241023
            WHERE source = %s AND tech_id IN %s AND `year` IN %s
        '''
        with connect.cursor() as cursor:
            cursor.execute(sql, (source, list_tech_id, list_time_slot))
            connect.commit()

            for i in cursor.fetchall():
                tech_id = int(i[0])
                year = int(i[1])
                count = int(i[2])
                if tech_id not in dict_tech_id_to_doc_count:
                    dict_tech_id_to_doc_count[tech_id] = [0]*len(list_time_slot)
                dict_tech_id_to_doc_count[tech_id][year-list_time_slot[0]] = count

        list_tech_id_to_doc_count_all_es.append(copy.deepcopy(dict_tech_id_to_doc_count))

    # ms
    dict_tech_id_to_doc_count_ms = {}
    sql = '''
        SELECT wid, `result` FROM lt_word_rank_20241023
        WHERE wid IN %s order by wid 
    '''
    with connect.cursor() as cursor:
        cursor.execute(sql, (list_tech_id, ))
        connect.commit()
        list_results = list(cursor.fetchall())

    connect.close()

    for i in list_results:
        tech_id = int(i[0])
        results = json.loads(i[1])
        temp = [0]*len(list_time_slot)
        for j in results:
            if j['year'] not in list_time_slot:
                continue
            else:
                temp[j['year']-list_time_slot[0]] = j['value']

        temp_copy = copy.deepcopy(temp)
        if tech_id not in dict_tech_id_to_doc_count_ms:
            dict_tech_id_to_doc_count_ms[tech_id] = temp_copy
        else:
            dict_tech_id_to_doc_count_ms[tech_id] = list(np.array(dict_tech_id_to_doc_count_ms[tech_id]) + np.array(temp_copy))

    dict_tech_id_to_doc_count = {}
    dict_tech_id_to_doc_count_es = list_tech_id_to_doc_count_all_es[0]
    for tech_id in dict_tech_id_to_doc_count_es:
        if tech_id in dict_tech_id_to_doc_count_ms:
            dict_tech_id_to_doc_count[tech_id] = list(np.array(dict_tech_id_to_doc_count_es[tech_id]) + np.array(dict_tech_id_to_doc_count_ms[tech_id]))
        else:
            dict_tech_id_to_doc_count[tech_id] = dict_tech_id_to_doc_count_es[tech_id]

    list_tech_id_to_doc_count_all_es[0] = dict_tech_id_to_doc_count
    return list_tech_id_to_doc_count_all_es


def calculate_hot_degree(list_time_slot, list_dict_tech_id_to_doc_count):
    hdce = HotDegreeComputingEngine(duration=2) # 计算通过相邻两个年度计算热度
    bias = 10

    list_dict_tech_id_to_hot_degree = []
    for dict_tech_id_to_doc_count in list_dict_tech_id_to_doc_count:
        dict_tech_id_to_hot_degree = {}

        # fixme 计算热度：每次取相邻两个年份的数据，计算后者年度的技术热度
        for i in range(len(list_time_slot) - 1):
            current_year = list_time_slot[i+1]
            dict_tech_id_to_doc_count_split = {} # 每次提取相邻两个
            for tech_id in dict_tech_id_to_doc_count:
                dict_tech_id_to_doc_count_split[tech_id] = \
                    dict_tech_id_to_doc_count[tech_id][i: i+2]

            flag = 'newton' # newton or integration
            dict_tech_id_to_hot_degree_in_current_year = hdce.bn_hot(
                dict_tech_id_to_doc_count_split, flag=flag
            )
            for tech_id in list(dict_tech_id_to_doc_count.keys()):
                if tech_id not in dict_tech_id_to_hot_degree:
                    dict_tech_id_to_hot_degree[tech_id] = []

                # temp_sigmoid = 100.0/(1.0 + math.exp(-dict_tech_id_to_hot_degree_in_current_year[tech_id]*0.9))
                # temp_sigmoid_cut = round(temp_sigmoid, 2)
                # dict_tech_id_to_hot_degree[tech_id].append(temp_sigmoid_cut)

                # temp_relu = round(5*max(dict_tech_id_to_hot_degree_in_current_year[tech_id] + bias, 0), 2)  # 0-20

                if dict_tech_id_to_doc_count_split[tech_id] == [0,0]:# 如果都是0，则热度为零
                    dict_tech_id_to_hot_degree[tech_id].append(round(0.0, 2))
                else:
                    temp_relu = round(max(dict_tech_id_to_hot_degree_in_current_year[tech_id]*5+50, 0), 2) #-10~10 -> 0~100
                    dict_tech_id_to_hot_degree[tech_id].append(temp_relu)

            # fixme 计算热度：每次取相邻两个年份的数据，计算后者年度的技术热度

        # 线性归一化
        dict_tech_id_to_hot_degree = linear_normalization(dict_tech_id_to_hot_degree)

        # fixme paper
        list_dict_tech_id_to_hot_degree.append(dict_tech_id_to_hot_degree)

    return list_dict_tech_id_to_hot_degree


def hot_degree(list_tech_id, years_span=10):
    year_end = datetime.date.today().year
    list_time_slot = [year for year in range(year_end-years_span, year_end + 1)]

    # {"技术词语1":[1,2,3,5,2,6,3...], "技术词语2":[1,2,3,5,2,6,3...], ...}
    list_dict_tech_id_to_doc_count = get_doc_count(list_tech_id, list_time_slot)

    # 第三步：计算技术词语的热度
    list_dict_tech_id_to_hot_degree = calculate_hot_degree(list_time_slot, list_dict_tech_id_to_doc_count)

    return list_dict_tech_id_to_hot_degree, list_time_slot


def calc(rows: list, target_key: str, *args, **kwargs):
    tech_ids = [row['golaxy_vocab_id'] for row in rows]
    res, years = hot_degree(tech_ids)
    paper, patent, news, project = res[0], res[1], res[2], res[3]
    ret = []
    for row in rows:
        tech_id = row['golaxy_vocab_id']
        new_row = dict(row)
        for year, s1, s2, s3, s4 in zip(years, paper[tech_id], patent[tech_id], news[tech_id], project[tech_id]):
            new_row['year'] = year
            new_row[f'{target_key}_paper'] = s1
            new_row[f'{target_key}_patent'] = s2
            new_row[f'{target_key}_news'] = s3
            new_row[f'{target_key}_project'] = s4

            ret.append(new_row)
    return ret
