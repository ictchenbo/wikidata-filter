"""通过这个模块设置组件的简名或别名，方便流程yaml中使用"""
from wikidata_filter.loader.wikidata import WikidataJsonDump, WikidataXmlIncr

base2 = "wikidata_filter.loader"

components = {
    f"{base2}.WikidataJsonDump": WikidataJsonDump,
    f"{base2}.WikidataXmlIncr": WikidataXmlIncr
}
