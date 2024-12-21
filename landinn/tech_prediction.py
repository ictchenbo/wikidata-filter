#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
import datetime
import copy
import pandas as pd
from statsmodels.tsa.stattools import adfuller as ADF
# from statsmodels.stats.diagnostic import acorr_ljungbox
# from statsmodels.graphics.tsaplots import plot_acf, plot_pacf #ACF与PACF
from statsmodels.tsa.arima.model import ARIMA #ARIMA模型

from landinn.util import get_conn

import warnings
warnings.filterwarnings("ignore")


def get_doc_count(list_tech_id, list_time_slot):
    # es
    list_tech_id_to_doc_count_all_es = []
    for source in ['paper']:
        dict_tech_id_to_doc_count = {}
        sql = '''
            SELECT tech_id, `year`, count FROM word_frequency_search_results_es_20241023
            WHERE source = %s AND tech_id IN %s AND `year` IN %s
        '''
        connect = get_conn()
        with connect.cursor() as cursor:
            cursor.execute(sql, (source, list_tech_id, list_time_slot))
            connect.commit()
            list_results = list(cursor.fetchall())
        connect.close()

        for i in list_results:
            tech_id = int(i[0])
            year = int(i[1])
            count = int(i[2])
            if tech_id not in dict_tech_id_to_doc_count:
                dict_tech_id_to_doc_count[tech_id] = [0]*len(list_time_slot)
            dict_tech_id_to_doc_count[tech_id][year-list_time_slot[0]] = count

        list_tech_id_to_doc_count_all_es.append(copy.deepcopy(dict_tech_id_to_doc_count))

    return list_tech_id_to_doc_count_all_es[0]


# 第三步函数
def calculate_technology_prediction(dict_tech_id_to_doc_count, list_time_slot):
    # 使用BIC矩阵计算p和q的值
    def cal_pqValue(D_data, diff_num=0):
        # 定阶
        pmax = int(len(D_data) / 10)  # 一般阶数不超过length/10
        qmax = int(len(D_data) / 10)  # 一般阶数不超过length/10
        bic_matrix = []  # BIC矩阵
        # 差分阶数
        diff_num = 2

        for p in range(pmax + 1):
            tmp = []
            for q in range(qmax + 1):
                try:
                    tmp.append(ARIMA(D_data, order=(p, diff_num, q)).fit().bic)
                except Exception as e:
                    print(e)
                    tmp.append(None)
            bic_matrix.append(tmp)

        bic_matrix = pd.DataFrame(bic_matrix)  # 从中可以找出最小值
        p, q = bic_matrix.stack().idxmin()  # 先用stack展平，然后用idxmin找出最小值位置。
        # print(u'BIC最小的p值和q值为：%s、%s' % (p, q))
        return p, q

    # 计算时序序列模型
    def cal_time_series(data, forecast_num, year_end):
        diff_num = 0 # 差分阶数
        diff_data = data     # 差分数序数据
        ADF_p_value = ADF(data[u'deal_data'])[1]
        while  ADF_p_value > 0.01:
            diff_data = diff_data.diff(periods=1).dropna()
            diff_num = diff_num + 1
            ADF_result = ADF(diff_data[u'deal_data'])
            ADF_p_value = ADF_result[1]
            # print("ADF_p_value:{ADF_p_value}".format(ADF_p_value=ADF_p_value))
            # print(u'{diff_num}差分的ADF检验结果为：'.format(diff_num = diff_num), ADF_result )
            if diff_num == 15:
                break

        # 使用BIC矩阵来计算q和p的值
        pq_result = cal_pqValue(diff_data, diff_num)
        p = pq_result[0]
        q = pq_result[1]

        # 构建时间序列模型
        model = ARIMA(data, order=(p, diff_num, q), enforce_stationarity=False).fit()  # 建立ARIMA(p, diff+num, q)模型
        # print('模型报告为：\n', model.summary())

        list_predict_value = list(model.forecast(forecast_num))
        list_predict_value = [int(i) if int(i) >= 0 else 0 for i in list_predict_value]
        list_year = [str(year) for year in range(year_end + 1, year_end + forecast_num + 1)]
        dict_year_to_predicted_doc_count = dict(map(lambda x, y:[x,y], list_year, list_predict_value))
        # print("预测结果：\n", dict_year_to_predicted_doc_count)
        return dict_year_to_predicted_doc_count

    def cal_threshold(list_doc_count):
        list_D_value = []
        for i in range(1, len(list_doc_count)):
            list_D_value.append(list_doc_count[i] - list_doc_count[i-1])

        average_value = sum(list_D_value)/len(list_D_value)
        list_upper_value = [x for x in list_D_value if x >= average_value]
        list_lower_value = [x for x in list_D_value if x < average_value]

        list_D_upper_value = [x-average_value for x in list_upper_value] # 都是正数
        list_D_lower_value = [x-average_value for x in list_lower_value] # 都是负数

        if list_D_lower_value == [] or list_D_lower_value == []:
            return -1,-1,-1

        upper_threshold = sum(list_D_upper_value)/len(list_D_upper_value)
        lower_threshold = sum(list_D_lower_value)/len(list_D_lower_value)
        return upper_threshold, lower_threshold, average_value

    def cal_trend1(list_predicted_doc_count, current_doc_count, upper_threshold, lower_threshold, average_value):
        value1 = list_predicted_doc_count[0]
        value2 = list_predicted_doc_count[1]
        value3 = list_predicted_doc_count[2]

        D_value1 = value1 - current_doc_count
        D_value2 = value2 - value1
        D_value3 = value3 - value2

        T_value1 = D_value1 - average_value
        T_value2 = D_value2 - average_value
        T_value3 = D_value3 - average_value

        if D_value1 > 0 and D_value2 > 0 and D_value3 > 0:# 逐渐增加
            if T_value1 > upper_threshold and T_value2 > upper_threshold and T_value3 > upper_threshold:
                return "快速上升"
            elif T_value1 < lower_threshold and T_value2 < lower_threshold and T_value3 < lower_threshold:
                return "缓慢上升"
            else:
                return "平稳上升"
        elif D_value1 < 0 and D_value2 < 0 and D_value3 < 0: # 逐渐减少
            if T_value1 > upper_threshold and T_value2 > upper_threshold and T_value3 > upper_threshold:
                return "缓慢下降"
            elif T_value1 < lower_threshold and T_value2 < lower_threshold and T_value3 < lower_threshold:
                return "快速下降"
            else:
                return "平稳下降"
        else:
            if T_value1 < upper_threshold and T_value2 < upper_threshold and T_value3 < upper_threshold \
                    and T_value1 > lower_threshold and T_value2 > lower_threshold and T_value3 > lower_threshold:
                return "平稳状态"
            else:
                return "无法判断"

    def cal_trend2(list_predicted_doc_count):
        value1 = list_predicted_doc_count[0]
        value2 = list_predicted_doc_count[1]
        value3 = list_predicted_doc_count[2]

        D_value12 = value2 - value1
        D_value23 = value3 - value2

        if D_value12 > 0 and D_value23 > 0:# 逐渐增加
            if D_value12 < D_value23:
                return "快速上升"
            elif D_value12 > D_value23:
                return "缓慢上升"
            else:
                return "平稳上升"
        elif D_value12 < 0 and D_value23 < 0: # 逐渐减少
            if D_value12 > D_value23:
                return "快速下降"
            elif D_value12 < D_value23:
                return "缓慢下降"
            else:
                return "平稳下降"
        else:
            average_value = float(sum(list_predicted_doc_count))/float(len(list_predicted_doc_count))
            average_D = (abs(float(D_value12)) + abs(float(D_value23)))/float(2.0)
            if average_value == 0:
                return "平稳状态"
            p = average_D/average_value
            if p < 0.15:
                return "平稳状态"
            else:
                return "无法判断"

    dict_tech_id_to_technology_prediction = {}
    for tech_id in dict_tech_id_to_doc_count:
        list_doc_count = dict_tech_id_to_doc_count[tech_id]
        year_end = list_time_slot[-1]
        if sum(list_doc_count) <= len(list_doc_count):
            dict_tech_id_to_technology_prediction[tech_id] = [year_end, {}, '', '', '1']
            continue
        list_small_value = [value for value in list_doc_count if value < 10]
        if len(list_small_value) >= int(len(list_time_slot)/2):# 一半及以上是小数字
            dict_tech_id_to_technology_prediction[tech_id] = [year_end, {}, '', '', '1']
            continue

        # 数据准备
        data = {'time_data': list_time_slot, 'deal_data': list_doc_count}
        df = pd.DataFrame(data)
        df.set_index(['time_data'], inplace=True)  # 设置索引

        # 计算预测值
        dict_year_to_predicted_doc_count = cal_time_series(df, 3, year_end) # 模型调用

        list_values = list(dict_year_to_predicted_doc_count.values())
        if sum(list_values) == 0:
            dict_tech_id_to_technology_prediction[tech_id] = [year_end, {}, '', '', '1']
            continue

        # 判断当前趋势
        current_trends = cal_trend2(list_doc_count[-3:])

        # 判断未来三年趋势
        predicted_trends = cal_trend2(list(dict_year_to_predicted_doc_count.values()))

        dict_tech_id_to_technology_prediction[tech_id] = [year_end, dict_year_to_predicted_doc_count, current_trends, predicted_trends, '0']

    return dict_tech_id_to_technology_prediction
    # fixme 真正计算新兴度 #########################################################################


# 主函数
def technology_prediction(list_tech_id: list, years_span=10):
    year_end = datetime.date.today().year
    list_time_slot = [year for year in range(year_end - years_span + 1, year_end + 1)]

    # 第2.1步：获取技术词语的词频
    # {"技术词语1":[1,2,3,5,2,6,3...], "技术词语2":[1,2,3,5,2,6,3...], ...}
    dict_tech_id_to_doc_count = get_doc_count(list_tech_id, list_time_slot)

    history_values = {}

    for tech_id in list_tech_id:
        list_historical_value = dict_tech_id_to_doc_count[tech_id]
        historical_value = {}
        for index in range(len(list_time_slot)):
            k = list_time_slot[index]
            v = list_historical_value[index]
            if k not in historical_value:
                historical_value[k] = v

        history_values[tech_id] = historical_value

    # 第2.2步：技术预测
    # {"技术词语id1":[year, maturity_degree, dict_date_to_doc_count_total_predict], "技术词语id2":[year, maturity_degree, dict_date_to_doc_count_total_predict], ...}
    dict_tech_id_to_technology_prediction = calculate_technology_prediction(dict_tech_id_to_doc_count, list_time_slot)

    return history_values, dict_tech_id_to_technology_prediction


def calc(row: dict, *, id_key: str = 'golaxy_vocab_id', result_key: str = 'predict', **kwargs):
    tech_id = row[id_key]
    history_values, res = technology_prediction([tech_id])
    history_values = history_values[tech_id]
    year, predicted_value, current_trends, predicted_trends, flag = res[tech_id]

    row[result_key] = dict(year=year, historical_value=history_values, predicted_value=predicted_value,
                current_trends=current_trends, predicted_trends=predicted_trends, flag=flag)

    return row
