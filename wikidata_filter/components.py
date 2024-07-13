from wikidata_filter.loader import *
from wikidata_filter.loader.database import *
from wikidata_filter.loader.wikidata import *

from wikidata_filter.iterator import *
from wikidata_filter.iterator.wikidata import *
from wikidata_filter.iterator.database import *
from wikidata_filter.matcher import *


base1 = "wikidata_filter.iterator"
base2 = "wikidata_filter.loader"
base3 = "wikidata_filter.matcher"


packages: dict = {
    "processor": base1,
    "loader": base2,
    "matcher": base3
}

components = {
    f"{base1}.Group": Group,
    f"{base1}.Chain": Chain,
    f"{base1}.Repeat": Repeat,
    f"{base1}.Filter": Filter,
    f"{base1}.Print": Print,
    f"{base1}.Count": Count,
    f"{base1}.Buffer": Buffer,
    f"{base1}.Select": Select,
    f"{base1}.Map": Map,
    f"{base1}.RemoveFields": RemoveFields,
    f"{base1}.FillField": FillField,
    f"{base1}.UpdateFields": UpdateFields,
    f"{base1}.CopyFields": CopyFields,
    f"{base1}.WriteJson": WriteJson,
    f"{base1}.WriteCSV": WriteCSV,
    f"{base1}.wikidata.IDNameMap": IDNameMap,
    f"{base1}.wikidata.Simplify": Simplify,
    f"{base1}.wikidata.SimplifyProps": SimplifyProps,
    f"{base1}.wikidata.ObjectNameInject": ObjectNameInject,
    f"{base1}.wikidata.ObjectAbstractInject": ObjectAbstractInject,
    f"{base1}.wikidata.AsRelation": AsRelation,
    f"{base1}.wikidata.ChineseSimple": ChineseSimple,
    f"{base1}.database.CKWriter": CKWriter,
    f"{base1}.database.ESWriter": ESWriter,

    f"{base2}.RandomGenerator": RandomGenerator,
    f"{base2}.JsonLineFileLoader": JsonLineFileLoader,
    f"{base2}.JsonArrayLoader": JsonArrayLoader,
    f"{base2}.database.CKLoader": CKLoader,
    f"{base2}.database.ESLoader": ESLoader,
    f"{base2}.database.MongoLoader": MongoLoader,
    f"{base2}.wikidata.WikidataJsonDump": WikidataJsonDump,
    f"{base2}.wikidata.WikidataXmlIncr": WikidataXmlIncr,

    f"{base3}.SimpleJsonMatcher": SimpleJsonMatcher,
    f"{base3}.JsonPathMatcher": JsonPathMatcher
}
