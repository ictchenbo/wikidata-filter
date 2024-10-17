from wikidata_filter.loader import *
from wikidata_filter.loader.database import *
from wikidata_filter.loader.wikidata import *

from wikidata_filter.iterator import *
from wikidata_filter.iterator.wikidata import *
from wikidata_filter.iterator.database import *
from wikidata_filter.matcher import *
from wikidata_filter.matcher.wikidata import WikidataMatcherV1, WikidataMatcherV2

from wikidata_filter.util import SetFromCSV, SetFromJSON, KVFromCSV, KVFromJSON


base1 = "wikidata_filter.iterator"
base2 = "wikidata_filter.loader"
base3 = "wikidata_filter.matcher"
base4 = "wikidata_filter.util"


components = {
    f"{base2}.RandomGenerator": RandomGenerator,
    f"{base2}.TxtLoader": TxtLoader,
    f"{base2}.JsonLineFileLoader": JsonLineFileLoader,
    f"{base2}.JsonLoader": JsonLoader,
    f"{base2}.JsonArrayLoader": JsonArrayLoader,
    f"{base2}.CSVLoader": CSVLoader,
    f"{base2}.ExcelLoader": ExcelLoader,
    f"{base2}.WikidataJsonDump": WikidataJsonDump,
    f"{base2}.WikidataXmlIncr": WikidataXmlIncr,
    f"{base2}.database.CKLoader": CKLoader,
    f"{base2}.database.ESLoader": ESLoader,
    f"{base2}.database.MongoLoader": MongoLoader,
    f"{base2}.database.MySQLLoader": MySQLLoader,
    f"{base2}.database.PostgresSQLLoader": PostgresSQLLoader,

    f"{base3}.SimpleJsonMatcher": SimpleJsonMatcher,
    f"{base3}.JsonPathMatcher": JsonPathMatcher,
    f"{base3}.WikidataMatcherV1": WikidataMatcherV1,
    f"{base3}.WikidataMatcher": WikidataMatcherV2,

    f"{base1}.Group": Group,
    f"{base1}.Chain": Chain,
    f"{base1}.Repeat": Repeat,
    f"{base1}.Filter": Filter,
    f"{base1}.Prompt": Prompt,
    f"{base1}.Print": Print,
    f"{base1}.Count": Count,
    f"{base1}.Buffer": Buffer,
    f"{base1}.Select": Select,
    f"{base1}.SelectVal": SelectVal,
    f"{base1}.Map": Map,
    f"{base1}.Flat": Flat,
    f"{base1}.FlatMap": FlatMap,
    f"{base1}.GroupBy": GroupBy,
    f"{base1}.RemoveFields": RemoveFields,
    f"{base1}.FillField": InjectField,
    f"{base1}.FieldJson": FieldJson,
    f"{base1}.AddFields": AddFields,
    f"{base1}.UpdateFields": UpdateFields,
    f"{base1}.ReverseKV": ReverseKV,
    f"{base1}.RuleBasedTransform": RuleBasedTransform,
    f"{base1}.WriteJson": WriteJson,
    f"{base1}.WriteCSV": WriteCSV,
    f"{base1}.IDNameMap": IDNameMap,
    f"{base1}.Simplify": Simplify,
    f"{base1}.SimplifyProps": SimplifyProps,
    f"{base1}.PropsFilter": PropsFilter,
    f"{base1}.ValuesFilter": ValuesFilter,
    f"{base1}.ObjectNameInject": ObjectNameInject,
    f"{base1}.ObjectAbstractInject": ItemAbstractInject,
    f"{base1}.AsRelation": AsRelation,
    f"{base1}.ChineseSimple": ChineseSimple,
    f"{base1}.database.CKWriter": CKWriter,
    f"{base1}.database.ESWriter": ESWriter,
    f"{base1}.database.MongoWriter": MongoWriter,

    f"{base4}.SetFromCSV": SetFromCSV,
    f"{base4}.SetFromJSON": SetFromJSON,
    f"{base4}.KVFromCSV": KVFromCSV,
    f"{base4}.KVFromJSON": KVFromJSON,
}
