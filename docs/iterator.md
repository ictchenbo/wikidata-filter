## 处理节点（Iterator）

模块：`wikidata_filter.iterator`

组件构造：`Comp(*args, **kwargs)` `iterator.<module>.<Comp>(*args, **kwargs)`


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


### 修改类
1. 投影操作 `Select(*keys)`
2. 数据映射转换 `Map(mapper)`
3. 移除字段 `RemoveFields(*keys)`
4. 重命名字段 `RenameFields(rename_template)`
5. 字段拷贝 `CopyFields(copy_template)`
6. 字段更新 `UpdateFields(update_template)`
7. 字段填充 `FillFields(kv,inject_path, reference_path)`


### 输出文件
1. JSON文件 `WriteJSON(output_file,append=False)`
2. CSV文件 `WriteCSV(output_file,keys=None,append=False)`


### 输出到数据库
1. ElasticSearch `iterator.database.ESWriter(host="localhost",port=9200,user=None,password=None,index=None,buffer_size=1000)`
2. ClickHouse `iterator.database.CKWriter(host='localhost',port=9000,user="default",password="",database='default',table=None, buffer_size=1000)`


### Wikidata处理
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

### 组合节点
1. 并行处理 `Group(*nodes)`
2. 串行处理 `Chain(*nodes)`
3. 重复数据 `Repeat(num_of_repeats)`

### Matcher
1. 简单JSON匹配 `matcher.SimpleJsonMatcher(match_rules)`
2. 基于`jsonpath`语法规则的匹配 `matcher.JsonPathMatcher(pattern)`
3. Wikidata基本匹配 `matcher.WikidataMatcherV1(match_relations)`
4. 针对简化wikidata匹配 `matcher.WikidataMatcher(match_relations)`
