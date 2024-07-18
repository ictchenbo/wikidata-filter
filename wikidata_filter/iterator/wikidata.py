from wikidata_filter.iterator.base import JsonIterator
from wikidata_filter.util.lang_util import zh_simple


def get_label(v):
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        return v["value"]
    return [vi["value"] if isinstance(vi, dict) else vi for vi in v]


def get_name(labels, keys, default=None):
    if labels is None:
        return default
    # 兼容非dict
    if not isinstance(labels, dict):
        return labels
    for key in keys:
        if key in labels:
            return get_label(labels[key])
    for key in labels.keys():
        return get_label(labels[key])

    return default


name_keys = ["zh-cn", "zh-hans", "zh-sg", "zh-hk", "zh-tw", "zh-mo", "en"]
wiki_sites = ["zhwiki", "enwiki"]


class IDNameMap(JsonIterator):
    """
    建立ID到name的映射
    """
    def on_data(self, item: dict or None, *args):
        return {
            "id": item["id"],
            "name": get_name(item.get('labels'), name_keys)
        }


class Simplify(JsonIterator):
    """
    对wikidata对象进行简化
    {id: str, labels: str, descriptions: str, aliases: list[str], claims: dict[str, list], sitelinks}
    """
    del_keys = ['type', 'title', 'ns', 'pageid']

    def on_data(self, item: dict or None, *args):
        if not item or not isinstance(item, dict):
            print("INVALID dict", item)
            return None
        for key in self.del_keys:
            if key in item:
                del item[key]
        # 支持重入
        item['labels'] = get_name(item.get('labels'), name_keys)
        item['descriptions'] = get_name(item.get('descriptions'), name_keys)
        item['aliases'] = get_name(item.get('aliases'), name_keys)

        # sitelink 最多保留一个
        if 'sitelinks' in item:
            sitelinks = item.pop('sitelinks')
            for site in wiki_sites:
                if site in sitelinks:
                    item['sitelinks'] = sitelinks[site]
                    break

        return item


def get_snak(snak):
    """
    snak中提取数据类型和数据值
    :param snak:
    :return:
    """
    _type = snak["snaktype"]

    if _type == "value" and "datavalue" in snak:
        datavalue = snak["datavalue"]
        vt, _value = datavalue["type"], datavalue["value"]
        if vt == "wikibase-entityid":
            _value = _value["id"]
        # elif vt == "globecoordinate":
        #     _value = [_value["latitude"], _value["longitude"]]
        # elif vt == "quantity":
        #     _value = _value["amount"]
        # elif vt == "time":
        #     _value = _value["time"]
        # elif vt == "monolingualtext":
        #     _value = f'{_value["language"]}:{_value["text"]}'

        return vt, _value

    return _type, None


def get_qualifiers(qs: dict):
    """
    获取属性的约束信息
    :param qs: 属性声明
    :return:
    """
    ret = {}
    for pid, snaks in qs.items():
        values = []
        for snak in snaks:
            _type, _value = get_snak(snak)
            if not _type or not _value:
                continue
            value = {
                "hash": snak["hash"],  # 属性属性的HASH值
                "datatype": _type,
                "datavalue": _value
            }
            values.append(value)
        ret[pid] = values
    return ret


def get_props(claims: dict):
    ret = {}
    # NOTICE: 可能为list 忽略错误
    if not claims or not isinstance(claims, dict):
        print('INVALID or EMPTY claims', claims)
        return ret
    for pid, claim_items in claims.items():
        values = []
        for claim in claim_items:
            _type, _value = get_snak(claim.get("mainsnak"))
            if not _type or not _value:
                continue
            prop = {
                "id": claim["id"],  # 属性claimID
                "datatype": _type,
                "datavalue": _value,
            }
            qs = get_qualifiers(claim.get("qualifiers", {}))
            if qs:
                prop['qualifiers'] = qs
            values.append(prop)
        ret[pid] = values
    return ret


class SimplifyProps(JsonIterator):
    """
    对原wikidata对象属性(claims)进行简化
    claims := dict[str, list[Prop]]
    Prop := {id: str, datatype: str, datavalue: PropVal,  qualifiers: dict[str, list[QProp]}
    QProp := {hash: str, datatype: PropDataType, datavalue: PropVal }
    PropDataType :=  wikibase-entityid | globecoordinate | quantity | time | monolingualtext | novalue | somevalue
    """
    def on_data(self, item: dict or None, *args):
        claims = get_props(item.get("claims", {}))
        item['claims'] = claims
        return item


class PropsFilter(JsonIterator):
    """
    对属性进行过滤 仅保留指定的属性列表
    """
    def __init__(self, props_set: set = None, props_list_file: str = None):
        props_set = props_set or set()
        if props_list_file:
            from wikidata_filter.util.file_loader import SetFromCSV
            props_set.update(SetFromCSV(props_list_file))
        self.props_set = props_set

    def on_data(self, item: dict or None, *args):
        new_claims = {}
        for key, vals in item.get("claims", {}).items():
            if key in self.props_set:
                new_claims[key] = vals

        item['claims'] = new_claims

        return item


class ValuesFilter(PropsFilter):
    """
    对属性值进行过滤 仅保留指定对象的属性
    """
    def __init__(self, props_set: set = None, props_list_file: str = None):
        super().__init__(props_set=props_set, props_list_file=props_list_file)

    def on_data(self, item: dict or None, *args):
        new_claims = {}
        for key, vals in item.get("claims", {}).items():
            new_vals = [val for val in vals if val.get("datatype") == "wikibase-entityid" and val["datavalue"] in self.props_set]
            if new_vals:
                new_claims[key] = new_vals

        if len(new_claims) == 0:
            return None

        item['claims'] = new_claims
        return item


class ObjectNameInject(JsonIterator):
    """
    基于给定的KV缓存 对当前实体的属性值实体增加其名称
    """
    FILL_KEY = 'labels'

    def __init__(self, kv: dict):
        self.kv = kv

    def fill_val(self, target: dict):
        if target["datatype"] in ["item", "wikibase-entityid"] and target.get("datavalue") in self.kv:
            ref_key = target.get("datavalue")
            # print('filled', ref_key)
            target[self.FILL_KEY] = self.kv[ref_key]

    def on_data(self, item: dict or None, *args):
        for prop, claims in item.get('claims', {}).items():
            for claim in claims:
                self.fill_val(claim)
                for sub_prop, sub_claims in claim.get('qualifiers', {}).items():
                    for sub_claim in sub_claims:
                        self.fill_val(sub_claim)

        return item


class ItemAbstractInject(JsonIterator):
    """
    基于给定的KV缓存 对当前实体获取其对应摘要信息填充
    kv: {'enwiki': {'Alfred Hitchcoc': 'Master of Suspense (album)' }, 'zhwiki': {} }
    """
    def __init__(self, kv: dict, source_key='sitelinks', fill_key='abstract'):
        self.kv = kv
        self.source_key = source_key
        self.fill_key = fill_key

    def on_data(self, item: dict or None, *args):
        if self.source_key in item:
            site = item[self.source_key]
            sitename = site["site"]
            pagetitle = site["title"]

            if sitename in self.kv:
                site_data = self.kv[sitename]
                if pagetitle in site_data:
                    item[self.fill_key] = site_data[pagetitle]

        return item


class ChineseSimple(JsonIterator):
    keys = ['labels', 'descriptions', 'abstract']

    def on_data(self, item: dict or None, *args):
        for key in self.keys:
            if key in item and item[key]:
                item[key] = zh_simple(item[key])

        for prop, claims in item.get('claims', {}).items():
            for claim in claims:
                if claim.get('labels'):
                    claim['labels'] = zh_simple(claim['labels'])

        return item


class AsRelation(JsonIterator):
    """
    转换为关系结构
    """
    def __init__(self):
        super().__init__()
        self.return_multiple = True

    def on_data(self, item: dict or None, *args):
        subject_id = item["id"]
        subject_name = item.get("labels")
        claims = item.get('claims', {})
        for relation, objects in claims.items():
            for obj in objects:
                yield {
                    "_id": obj["id"],
                    "subject_id": subject_id,
                    "subject_name": subject_name,
                    "relation": relation,
                    "object_id": obj["datavalue"],
                    "object_name": obj.get("labels")
                }
