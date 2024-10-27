"""通过这个模块设置组件的简名或别名，方便流程yaml中使用"""
from wikidata_filter.loader.wikidata import WikidataJsonDump, WikidataXmlIncr
from wikidata_filter.iterator.wikidata import *
from wikidata_filter.iterator.matcher import WikidataMatcherV2


base1 = "wikidata_filter.iterator"
base2 = "wikidata_filter.loader"
base4 = "wikidata_filter.util"


components = {
    f"{base1}.IDNameMap": IDNameMap,
    f"{base1}.Simplify": Simplify,
    f"{base1}.SimplifyProps": SimplifyProps,
    f"{base1}.PropsFilter": PropsFilter,
    f"{base1}.ValuesFilter": ValuesFilter,
    f"{base1}.ObjectNameInject": ObjectNameInject,
    f"{base1}.ObjectAbstractInject": ItemAbstractInject,
    f"{base1}.AsRelation": AsRelation,
    f"{base1}.ChineseSimple": ChineseSimple,
    f"{base1}.matcher.WikidataMatcher": WikidataMatcherV2,

    f"{base2}.WikidataJsonDump": WikidataJsonDump,
    f"{base2}.WikidataXmlIncr": WikidataXmlIncr
}
