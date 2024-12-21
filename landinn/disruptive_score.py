import json
import math
from landinn.util import get_conn


CH1 = 'arxiv'
CH2 = 'google_scholar'

MAP1 = {}
MAP2 = {}
MAPS = {
    CH1: MAP1,
    CH2: MAP2
}


def doc_count_from_mysql():
    sql = "select word,lang,result,source from lt_word_rank_20241023"
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(sql)
    for row in cursor.fetchall():
        word, lang, result, source = row
        MAPS[source][word] = json.loads(result)

    cursor.close()
    conn.close()


doc_count_from_mysql()


def fun_judge_word_include_list(_w, _list):
    for _str in _list:
        if _str in _w:
            return True
    return False


# 过滤规则
def rule1(_w):
    """
    过滤规则
    :param _w: 输入技术词
    :return:返回过滤权重值
    """
    _not_all = ['显微镜', '算法', '方法', '追踪', '刀库', '算子', '方法', '推力', '导引', '外洗', '算法模型',
                '改进算法',
                '优化算法', '算法优化', '算法改进', '模型', '构型', '小车', '递归', '吻合', '再入防护']
    _not_end_0 = [
        '壳体', '端', '端口', '效率', '性', '成本', '程度', '率', '度', '步骤', '能力', '板', '大棚', '效果',
        '中心', '平台', '结果', '桌板', '指标', '技术量', '设备', '性能', '阈值', '时长', '均衡', '槽', '地图',
        '诊断', '温度', '能力', '信息', '性价比', '箱体', '净水器', '半径', '定标', '矫正', '制图', '公司',
        '时间', '带宽', '条件', '分束比', '能力', '参数', '直径', '要求', '色谱柱', '槽体', '结构', '腔室',
        '损失', '工位', '频率', '样品台', '排气口', '入口', '速度', '漏电', '组件', '干燥腔', '工件', '模块',
        '面积', '应力', '腐蚀液', '侧门', '平面', '机构', '质量', '费用', '效应', '偏差', '误差', '获取',
        '评价', '面积比', '谈判', '时长', '烘烤', '记录', '制造', '建筑', '设施', '批发', '零售',
        '策略', '样本', '数据', '字符', '提供方', '底座', '再入防护'
    ]
    _not_start_0 = [
        '以下', '获取', '输入', '本发明', '长期使用', '本程序', '本软件', '该', '较为', '前者', '步骤', '此'
    ]
    _not_end_0_9 = [
        '领域', '通道', '屏', '评估', '分析', '介质', '原理', '工艺', '零件', '室', '炉', '箱', '电源',
        '胶', '电极', '管', '层', '杆', '盘', '阀', '器', '图', '体系', '策略', '框架', '系统', '充电桩', '抗雷击技术'
    ]
    _not_end_0_85 = ['预处理', '网络', '地图', '装置', '部件', '主轴', '流量回溯', '动力装置与能源']
    _not_end_0_7 = [
        '加工', '地图', '装置', '部件', '装备', '锻件', '建筑材料', '原材料', '資料模組', '服务器柜',
        '代码编程', '测试台架', '接头', '主体', '上盖', '机身'
    ]

    _not_end_0_5 = ['单元', '软件', '训练', '产品', '铸件', '采运']

    # 判断是否是非颠覆性
    if _w.endswith('方法'):
        if len(_w) <= 5:
            return 0
        else:
            return 0.85

    if _w in _not_all:
        return 0

    for ii in range(len(_not_end_0)):
        if _w.endswith(_not_end_0[ii]):
            return 0

    for ii in range(len(_not_start_0)):
        if _w.startswith(_not_start_0[ii]):
            return 0

    for ii in range(len(_not_end_0_9)):
        if _w.endswith(_not_end_0_9[ii]):
            return 0.9

    for ii in range(len(_not_end_0_85)):
        if _w.endswith(_not_end_0_85[ii]):
            return 0.85

    for ii in range(len(_not_end_0_5)):
        if _w.endswith(_not_end_0_5[ii]):
            return 0.5
    if len(_w) > 10:
        return 1.1
    return 1


# 优化规则：根据人工词库里，对颠覆性进行二次优化
def rule2(_w, _score):
    if _score == 0:
        return 0
    _words_90_in = [
        'gpt', 'GPT', '3D打印', '纳米材料', '纳米尺度', '纳米粉体', '高精度纳米', '纳米复合材料', '三维纳米',
        '纳米光刻', '高熵合金', '元宇宙', '多语言处理', '语法纠错', '光子加密', '注意力机制', '微电子干扰',
        '量子干涉', '量子线路', '量子纠缠', '量子叠加', '量子芯片', '量子纠错', '量子密钥', '量子态操控', '量子效应',
        '原子干涉仪', '态势感知', '无人驾驶', '自动驾驶', '脑电信号采集', 'DNA修复', '基因整合', '人工细胞', '基因修饰',
        '基因沉默'
    ]
    _words_85_in = [
        '量子导航', '量子点传感', '量子态传输', '基因修复', '智能传感', '基因组编辑', '细胞疗法', '核动力系统'
    ]
    _words_90 = [
        '大模型', '时空学习', '类脑芯片', '神经形态工程', '脑机接口', '神经机器接口', '脑控技术', '多基因工程', '边缘计算技术',
        '人工智能'
    ]
    _words_80 = [
        '零样本', '硅神经元', '多语言支持', '区块链技术', '脑皮层信号采集', '预训练模型', '多方安全计算(MPC)',
        '微波扫描仪', '共识算法', '多角度目标定位'
    ]

    out = _score
    if fun_judge_word_include_list(_w, _words_90_in):
        out = 0.9 + 0.1 * _score
    elif fun_judge_word_include_list(_w, _words_85_in):
        out = 0.85 + 0.15 * _score
    elif _w in _words_90:
        out = 0.9 + 0.1 * _score
    elif _w in _words_80:
        out = 0.8 + 0.2 * _score
    return out
    pass


# 颠覆性得分计算函数
def cal_k_new(_d, _word):
    """
    计算技术突变性得分
    :param _d: 字典，key为年份，升序排列，value为该年数据的数量
    :param _word: 技术词
    :return: 返回技术突变型得分
    """
    if _word.lower() == 'chatgpt':
        return 0.9849645338468924

    if _d == {}:
        return -1

    # 仅保留保留输入字典中2009年后的数据
    _d_use = {}
    for _t in _d.keys():
        if int(_t) >= 2009:
            _d_use[int(_t)] = _d[_t]

    # 按照时间顺序提取出数量
    _key_list = [int(k) for k in _d_use.keys()]
    _val_list = [_d_use[k] for k in _d_use.keys()]

    # 计算技术生长率得分
    _score_k = 0
    _year_change = 2024
    if len(_val_list) > 1:
        for _i in range(1, len(_val_list)):
            if _val_list[_i - 1] == 0:
                continue
            tem_del = (_val_list[_i] - _val_list[_i - 1]) / _val_list[_i - 1]
            if tem_del >= _score_k:
                _score_k = tem_del
                _year_change = _key_list[_i]

    # 归一化
    _out = math.degrees(math.atan(_score_k)) * (0.01 * _year_change - 19.24) / 90

    # 过滤加权
    _r = rule1(_word)
    _out = _r * _out

    # 针对人工数据库里的颠覆性词进行二次优化
    _out2 = rule2(_word, _out)

    return _out2


# 三个来源按照权重加权求值
def cal_weight(_arr):
    """
    :param _arr: [paper, patent, news]
    :return:
    """
    _arr_set = set(_arr)
    if _arr_set == {0, -1}:
        return 0.0
    if _arr_set == {0}:
        return 0.0
    if _arr_set == {-1}:
        return 0.0  # 这个地方原来是 -1
    _arr_set.discard(-1)
    _arr_set.discard(0)
    return sum(_arr_set) / len(_arr_set)


def merge_values(values1: list, values2: list):
    ret = {}
    for v in (values1+values2):
        year, value = v['year'], v['value']
        if year in ret:
            ret[year] += value
        else:
            ret[year] = value
    return ret


def cal_score1(word_zh, word_en):
    value1 = merge_values(MAP1.get(word_zh) or [], MAP1.get(word_en) or [])

    value2 = merge_values(MAP2.get(word_zh) or [], MAP2.get(word_en) or [])

    _out = cal_weight([cal_k_new(value1, word_zh), cal_k_new(value2, word_zh)])

    _out = round(_out * 100, 3)

    if _out > 100:
        _out = 98 + (_out - int(_out))

    return _out


def calc(row: dict, *, result_key: str = 'node_score', **kwargs):
    name_zh, name_en = row['name_zh'], row['name_en']
    row[result_key] = cal_score1(name_zh, name_en)
    return row
