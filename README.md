# wikidata-filter
Wikidata与Wikipedia数据处理框架，提供Wikidata&Wikipedia Dump数据解析、转换处理、文件加载、数据库加载、文件输出、数据库输出等。

关于wikidata知识图谱的介绍，可以参考作者的一篇博客文章 https://blog.csdn.net/weixin_40338859/article/details/120571090

## New!
- 2024.10.24
1. 新增GDELT处理流程，持续下载[查看](flows/gdelt.yaml) 滚动下载export.CSV.zip文件
2. 增加新的Loader `GdeltTaskEmit` 从指定时间开始下载数据并持续跟踪
3. 新增经济学人民调数据处理算子 `iterator.web.polls.PollData` （需要手工下载CSV）、处理流程[查看](flows/load_polls.yaml)
4. 修改`Flat`算子逻辑，如果输入为`dict`，则提取k-v，如果v也是`dict，则作为

- 2024.10.17
1. 添加多个处理算子：FieldJson、Flat、FlatMap、AddFields [查看](docs/iterator.md)
2. 初步添加规约类算子：BufferBase Reduce GroupBy

- 2024.10.15
1. 修改CkWriter参数为 username tcp_port 明确使用TCP端口（默认9000，而不是HTTP端口8123）
2. 新增字段值 String -> Json 算子 `FieldJson(key)`
3. 新增加载json文件到ClickHouse流程[查看](flows/db_load_data_mongo_table.yaml)
4. 新增ClickHouse表复制的流程[查看](flows/db_copy_clickhouse.yaml)

- 2024.10.14
1. 新增 MongoWriter
2. 新增 MongoDB表复制流程[查看](flows/db_copy_mongo.yaml)

- 2024.10.02
1. WriteJson WriterCSV增加编码参数设置
2. 新增GDELT本地数据处理的简化流程[查看](flows/gdelt_local.yaml) 通过加载本地文件转化成JSON

- 2024.09.30
1. 集成Reader API（`wikidata_filter.iterator.web.readerapi` 详见 https://jina.ai/reader/)
2. 增减文本文件加载器 TxtLoader（详见 `wikidata_filter.loader.file.TxtLoader`）
3. 新增Reader API的流程 [查看](flows/crawl_webpage_readerapi.yaml) 加载url列表文件 实现网页内容获取


## 项目特色
1. 通过`yaml`格式定义流程，上手容易
2. 内置数十种ETL算子，配置简单
3. 支持常见数据库的读取和写入
4. 内置特色数据资源处理流程：
   - wikipedia 维基百科
   - wikidata 维基数据
   - GDELT 谷歌全球社会事件数据库 （流式，直接下载）
   - GTD 全球恐怖主义事件库 


## 核心概念
- Flow: 处理流程，实现数据载入（或生成）、处理、输出的过程
- Loader：数据加载节点（对应flume的`source`） 
- Iterator：数据处理节点，用于表示各种各样的处理逻辑，包括数据输出与写入数据库（对应flume的`sink`）  
- Matcher：数据匹配节点，是一类特殊的`Iterator`，可作为函数调用
- Engine：按照Flow的定义进行执行。简单Engine只支持单线程执行。高级Engine支持并发执行，并发机制通用有多线程、多进程等

## 快速使用
1. 安装依赖
```shell
 pip install -r requirements.txt
```

2. 流程定义

- 示例1：生成100个随机数并重复5遍 `flows/test_multiple.yaml`

```yaml
name: test multiple
nodes:
  n1: Repeat(5)
  n2: Count(ticks=5, label='Repeat')
  n3: Print

loader: RandomGenerator(100)
processor: Group(n1, n2, n3)

```

- 示例2：输入wikidata dump文件（gz/json）生成id-name映射文件（方便根据ID查询名称），同时对数据结构进行简化 `flows/p1_idname_simple.yaml`
```yaml
name: p1_idname_simple
arguments: 2

loader: WikidataJsonDump(arg1)

nodes:
  n1: IDNameMap
  n2: WriteJson('data/id-name.json')
  n3: Simplify
  n4: SimplifyProps
  n5: WriteJson(arg2)
  chain1: Chain(n1, n2)
  chain2: Chain(n3, n4, n5)

processor: Group(chain1, chain2)
```

- 示例3：基于wikidata生成简单图谱结构，包含Item/Property/Item_Property/Property_Property 四张表 `flows/p1_wikidata_graph.yaml`
```yaml
name: p1_wikidata_graph
description: transform wikidata dump to graph, including item/property/item_property/property_property
arguments: 5

loader: WikidataJsonDump(arg1)

nodes:
  writer1: WriteJson(arg2)
  writer2: WriteJson(arg3)
  writer3: WriteJson(arg4)
  writer4: WriteJson(arg5)

  rm_type: RemoveFields('_type')

  entity: iterator.wikidata_graph.Entity
  filter_item: "Filter(lambda p: p['_type']=='item')"
  filter_property: "Filter(lambda p: p['_type']=='property')"
  chain1: Chain(filter_item, rm_type, writer1)
  chain2: Chain(filter_property, rm_type, writer2)
  group1: Group(chain1, chain2)

  property: iterator.wikidata_graph.ItemProperty
  filter_item_property: "Filter(lambda p: p['_type']=='item_property')"
  filter_property_property: "Filter(lambda p: p['_type']=='property_property')"
  chain3: Chain(filter_item_property, rm_type, writer3)
  chain4: Chain(filter_property_property, rm_type, writer4)
  group2: Group(chain3, chain4)

  chain_entity: Chain(entity, group1)
  chain_property: Chain(property, group2)

processor: Group(chain_entity, chain_property)
```

3. 启动流程
**示例一**
```shell
 python main_flow.py flows/test_multiple.yaml
```

**示例二**
```shell
 python main_flow.py flows/p1_idname_simple.yaml dump.json simple.json
```

**示例三**
```shell
 python main_flow.py flows/flows/p1_wikidata_graph.yaml dump.json item.json property.json item_property.json property_property.json
```

## 参考文档

YAML Flow [Flow 格式说明](docs/yaml-flow.md)

数据加载器 [Loader 说明文档](docs/loader.md)

处理节点（过滤、转换、输出等） [Iterator 说明文档](docs/iterator.md)

辅助函数 [util 说明文档](docs/util.md)


## 更多信息

详细设计说明[设计文档](docs/main-design.md)

Flow流程配置设计[可配置流程设计](docs/yaml-flow-design.md)
