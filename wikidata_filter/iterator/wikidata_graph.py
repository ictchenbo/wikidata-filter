from wikidata_filter.iterator.edit import Map, Flat
from wikidata_filter.iterator.wikidata import get_name, get_snak


name_keys = ["zh-cn", "zh-hk", "zh", "en"]
name_en_keys = ["en"]


class Entity(Map):
    """
    输出wikidata item/property基本信息
    """
    def on_data(self, entity: dict, *args):
        if "labels" not in entity or "descriptions" not in entity:
            return None
        eid = entity["id"]
        return {
            "_id": int(eid[1:]),
            "_type": entity.get("type") or "item",
            "id": eid,
            # "modified": entity["modified"],
            "name": get_name(entity.get("labels"), name_keys),
            "name_en": get_name(entity.get("labels"), name_en_keys),
            "desc": get_name(entity.get("descriptions"), name_keys),
            "desc_en": get_name(entity.get("descriptions"), name_en_keys),
            "aliases": get_name(entity.get("aliases"), name_keys)
        }


def get_props(item):
    qid = item["id"]
    claims = item.get("claims", {})
    # print(claims)
    for pid in claims.keys():
        claim_items = claims[pid]
        if isinstance(claim_items, dict):
            claim_items = [claim_items]
        for claim in claim_items:
            _type, _value = get_snak(claim.get("mainsnak"))
            if not _type or not _value:
                continue
            prop = {
                "id": claim["id"],  # 属性claimID
                "qid": qid,  # item ID
                "pid": pid,  # 属性ID
                "datatype": _type,
                "datavalue": _value
            }
            prop_props = list(get_qualifiers(claim, pid))
            yield prop, prop_props


def get_qualifiers(claim, pid):
    """
    获取属性的属性
    :param claim: 属性声明
    :param pid: 属性id
    :return:
    """
    cid = claim["id"]
    qs = claim.get("qualifiers", {})
    for pid2, snaks in qs.items():
        for snak in snaks:
            _type, _value = get_snak(snak)
            if not _type or not _value:
                continue
            yield {
                "id": cid,  # 属性claimID
                "hash": snak["hash"],  # 属性属性的HASH值
                "pid": pid,  # 属性ID
                "ppid": pid2,  # 属性属性ID
                "datatype": _type,
                "datavalue": _value
            }


class ItemProperty(Flat):
    """
    输出wikidata的实体属性和属性属性
    """
    def on_data(self, entity: dict, *args):
        if entity["type"] != "item":
            return None
        for prop, prop_props in get_props(entity):
            prop["_type"] = "item_property"
            yield prop
            for prop_prop in prop_props:
                prop_prop["_type"] = "property_property"
                yield prop_prop


class Relation(Flat):
    """
    转换为关系结构
    """
    def on_data(self, item: dict, *args):
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
