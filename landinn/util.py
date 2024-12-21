import pymysql
from .config import *


def get_conn(database=DATABASE):
    conn = pymysql.connect(host=HOST,
                           port=PORT,
                           user=USER,
                           password=PASSWORD,
                           database=database,
                           charset="utf8mb4"
                           )
    return conn


def get_tech_words():
    sql_research_word = '''
        SELECT distinct golaxy_vocab_id, name_zh, name_en, tech_domain
        FROM lanting_words_20241023
        '''
    connect = get_conn()
    cursor = connect.cursor()
    cursor.execute(sql_research_word)
    list_tech_words = cursor.fetchall()
    list_tech_id = []
    dict_tech_id_to_tech_name_ch = {}
    dict_tech_id_to_tech_name_en = {}
    dict_tech_id_to_tech_domain = {}
    # length = len(list_tech_words)
    # index = 1
    for i in list_tech_words:
        # print('{}/{}'.format(index, length))
        # index += 1
        tech_id = int(i[0]) # 技术id
        tech_name_ch = i[1] # 技术名称，一般是中文
        tech_name_en = i[2] # 英文技术名称
        tech_domain = i[3]
        if tech_id in list_tech_id:
            continue
        list_tech_id.append(tech_id)
        dict_tech_id_to_tech_name_ch[tech_id] = tech_name_ch
        dict_tech_id_to_tech_name_en[tech_id] = tech_name_en
        dict_tech_id_to_tech_domain[tech_id] = tech_domain
    return list_tech_id, dict_tech_id_to_tech_name_ch, dict_tech_id_to_tech_name_en, dict_tech_id_to_tech_domain
