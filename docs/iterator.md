## 处理节点（Iterator）

模块：`wikidata_filter.iterator`

组件构造：`Comp(*args, **kwargs)` `<module>.<Comp>(*args, **kwargs)`


### 基类设计
1. 抽象基类 `JsonIterator` 定义了数据处理的接口
```python
class JsonIterator:
    def on_start(self):
        pass

    def on_data(self, data: dict or None, *args):
        pass

    def on_complete(self):
        pass

    def return_multiple(self):
        return False
```


### 基础类
1. 打印数据 `Print` 方便调试或日志记录 无参数
2. 计数 `Count(ticks=1000, label='-')` 对数据进行统计，方便观察 参数：ticks、label
3. 过滤 `Filter(matcher)` 参数：过滤函数/Matcher对象 可参考[Matcher](#matcher)
4. 缓冲 `Buffer(batch_size=100)` 参数：缓冲一定数量数据后再一起推送

### Matcher（也是Filter）
1. 简单JSON匹配 `matcher.SimpleJsonMatcher(match_rules)`
2. 基于`jsonpath`语法规则的匹配 `matcher.JsonPathMatcher(pattern)`


### 修改类
1. 投影操作 `Select(*keys)`
2. 数据映射转换 `Map(mapper)`
3. 移除字段 `RemoveFields(*keys)`
4. 重命名字段 `RenameFields(**kwargs)`
5. 字段添加 `AddFields(**kwargs)`
6. 字段更新 `UpdateFields(**kwargs)`
7. 字段填充 `InjectField(kv,inject_path, reference_path)`
8. 对调KV `ReverseKV()`
9. 基于规则的转换 `RuleBasedTransform(rules)`
10. 字段扁平化 `Flat(key)`
11. 扁平化转换 `FlatMap(mapper)`
12. 字段作为JSON加载 `FieldJson(key)`
13. 按照某个字段对数据进行分组 `GroupBy(key)`

### 输出文件
1. JSON文件 `WriteJSON(output_file,append=False)`
2. CSV文件 `WriteCSV(output_file,keys=None,append=False)`


### 输出到数据库
1. ElasticSearch `database.ESWriter(host="localhost",port=9200,user=None,password=None,index=None,buffer_size=1000)`
2. ClickHouse `database.CKWriter(host='localhost',tcp_port=9000,username="default",password="",database='default',table=None, buffer_size=1000)`
3. MongoDB `database.MongoWriter(host='localhost',port=27017,username=None,password=None,database='default',auth_db='admin',collection=None,buffer_size=1000)`

### 组合节点
1. 并行处理 `Group(*nodes)`
2. 串行处理 `Chain(*nodes)`
3. 重复数据 `Repeat(num_of_repeats)`


### Wikidata处理
模块：`wikidata_filter.iterator.wikidata`

1. 生成ID-名称映射结构 `IDNameMap`
2. item字段简化，对labels/description/alias仅保留中文或英文 `Simplify`
3. 对item的属性进行简化  `SimplifyProps`
```textmate
    对原wikidata对象属性(claims)进行简化
    claims := dict[str, list[Prop]]
    Prop := {id: str, datatype: str, datavalue: PropVal,  qualifiers: dict[str, list[QProp]}
    QProp := {hash: str, datatype: PropDataType, datavalue: PropVal }
    PropDataType :=  wikibase-entityid | globecoordinate | quantity | time | monolingualtext | novalue | somevalue
```
4. 属性过滤器，仅保留具有特定属性（Pxx）的item `PropsFilter(props_set)`
5. 属性值过滤器，仅保留具有特定属性值（Qxx）的item `ValuesFilter(props_set)`
6. 属性对象名称注入，根据KV查询对象的名称进行注入 `ObjectNameInject(kv)`
7. item条目对应wikipedia页面摘要注入，根据KV查询维基页面摘要进行注入 `ObjectAbstractInject(kv)`
8. 对item的labels/descriptions/abstract字段转化为中文简体 `ChineseSimple`
9. 生成关系数据结构（**multiple**） `AsRelation`
10. Wikidata基本匹配 `matcher.WikidataMatcherV1(match_relations)`
11. 针对简化wikidata匹配 `matcher.WikidataMatcher(match_relations)` （也可以用`matcher.WikidataMatcherV2`）


### Wikidata知识图谱处理
模块：`wikidata_filter.iterator.wikidata_graph`

1. 生成Item和Property摘要 `wikidata_graph.Entity`
2. 生成实体Item：`wikidata_graph.Entity` -> `Filter(lambda p: p['_type']=='item')`
3. 生成属性Property：`wikidata_graph.Entity` -> `Filter(lambda p: p['_type']=='property')`
4. 提取实体属性：`wikidata_graph.ItemProperty` （结果根据`_type`区分为：item_property property_property）


### GDELT数据处理
模块：`wikidata_filter.iterator.web.gdelt`
1. 基于gdelt的更新文件（CSV.zip）及对应的schema文件生成json记录 `web.gdelt.Export(save_path=None)` save_path保存下载文件的路径

**说明** GDELT文件包括：
- 事件表 `event-table`（schema见`config/gdelt/export.schema`）
- 事件提到表 `mention-table` （schema见`config/gdelt/mention.schema`）
- 事件图谱 **TODO**
