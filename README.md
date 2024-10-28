# wikidata-filter
一个简单但是实用、灵活、可配置、开箱即用的Python数据处理框架，提供**Wikidata** / **Wikipedia** / **GDELT**等多种开源数据的处理流程；
支持txt/json/csv/excel等文件格式、MySQL/PostgreSQL/MongoDB/ClickHouse/ElasticSearch等数据库作为输入和输出；
提供**大模型**、**Web API**等多种处理算子

项目持续丰富中，欢迎反馈各类数据处理需求，持续丰富Data Intelligence

![系统使用](docs/img.png)

关于wikidata知识图谱的介绍，可以参考作者的一篇博客文章 https://blog.csdn.net/weixin_40338859/article/details/120571090

## New！
- 2024.10.28
1. 合并`Converter`、`FieldConverter`到`Map`算子，支持对字段进行转换，支持设置目标字段
2. 修改`Select`以支持嵌套字段`user.name.firstname`形式
3. 新增天玑大模型接口调用`GoGPT(api_base,field,ignore_errors,prompt)`
4. 新增一个[新闻处理流程](flows/news_process.yaml) 通过提示大模型实现新闻主题分类、地名识别并并建立ES索引
5. 新增文本处理算子模块 `iterator.nlp` 提供常用文本处理
6. 为基类`JsonIterator`增加_set链式方法，简化算子属性设置和子类实现（子类__init__不需要设置每个基类参数）比如可以写：`WriteJson('test_data/test.json')._set(buffer_size=50)`
7. 重新实现缓冲基类`Buffer`（具有一定大小的缓冲池）、缓冲写基类`BufferedWriter`，文本写基类`WriteText`继承`BufferedWriter`


- 2024.10.27
1. 修改`main_flow` 支持参数设置，详细查看帮助：`python main_flow.py -h` 支持通过命令行提供loader数据
2. 增加两个简单的loader组件：`ArrayProvider(arr)`、`TextProvider(txt, sep='\n')` 可参考[简单流程](flows/test_simple.yaml)
3. 简化各流程文件的参数设置 方便快速使用

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
- Matcher：数据匹配节点，是一类特殊的`JsonIterator`，可作为函数调用
- Engine：按照Flow的定义进行执行。简单Engine只支持单线程执行。高级Engine支持并发执行，并发机制通用有多线程、多进程等

## 快速使用
1. 安装依赖
```shell
 pip install -r requirements.txt
```

2. 查看帮助
```shell
 python main_flow.py -h
```

3. 流程定义

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
arguments: 1

loader: WikidataJsonDump(arg1)

nodes:
  n1: IDNameMap
  n2: WriteJson('data/id-name.json')
  n3: Simplify
  n4: SimplifyProps
  n5: WriteJson('test_data/p1.json')
  chain1: Chain(n1, n2)
  chain2: Chain(n3, n4, n5)

processor: Group(chain1, chain2)
```

- 示例3：基于wikidata生成简单图谱结构，包含Item/Property/Item_Property/Property_Property 四张表 `flows/p1_wikidata_graph.yaml`
```yaml
name: p1_wikidata_graph
description: transform wikidata dump to graph, including item/property/item_property/property_property
arguments: 1

loader: WikidataJsonDump(arg1)

nodes:
  writer1: WriteJson('test_data/item.json')
  writer2: WriteJson('test_data/property.json')
  writer3: WriteJson('test_data/item_property.json')
  writer4: WriteJson('test_data/property_property.json')

  rm_type: RemoveFields('_type')

  entity: wikidata_graph.Entity
  filter_item: "Filter(lambda p: p['_type']=='item')"
  filter_property: "Filter(lambda p: p['_type']=='property')"
  chain1: Chain(filter_item, rm_type, writer1)
  chain2: Chain(filter_property, rm_type, writer2)
  group1: Group(chain1, chain2)

  property: wikidata_graph.ItemProperty
  filter_item_property: "Filter(lambda p: p['_type']=='item_property')"
  filter_property_property: "Filter(lambda p: p['_type']=='property_property')"
  chain3: Chain(filter_item_property, rm_type, writer3)
  chain4: Chain(filter_property_property, rm_type, writer4)
  group2: Group(chain3, chain4)

  chain_entity: Chain(entity, group1)
  chain_property: Chain(property, group2)

processor: Group(chain_entity, chain_property)
```

4. 启动流程
**示例一**
```shell
 python main_flow.py flows/test_multiple.yaml
```

**示例二**
```shell
 python main_flow.py flows/p1_idname_simple.yaml dump.json
```

**示例三**
```shell
 python main_flow.py flows/p1_wikidata_graph.yaml dump.json
```

## 使用者文档 User Guide

YAML Flow [Flow 格式说明](docs/yaml-flow.md)

数据加载器 [Loader 说明文档](docs/loader.md)

处理节点（过滤、转换、输出等） [Iterator 说明文档](docs/iterator.md)

辅助函数 [util 说明文档](docs/util.md)


## 开发者文档 Developer Guide

详细设计说明[设计文档](docs/main-design.md)

Flow流程配置设计[可配置流程设计](docs/yaml-flow-design.md)


## 开发日志
- 2024.10.26
1. 新增大模型处理算子`LLM` 可调用与OpenAI接口兼容的在线大模型接口，需要提供api_base、api_key，其他参数支持：model、proxy、prompt、temp等
2. 基于`LLM`实现月之暗面（Kimi）大模型`Moonshot`、Siliconflow平台大模型`Siliconflow`大模型算子
3. 新增大模型调用流程示例[查看](flows/test_llm.yaml) 填入api_key即可执行：`python main_flow.py flows/llm_local.yaml`
4. 增加一些测试流程的测试样例数据[查看](test_data)
5. 修改`JsonMatcher`，继承`Filter`，使得匹配对象可以直接作为过滤算子（之前是作为`Filter`的参数） `matcher`移动到`iterator`下
6. 简化iterator的配置，nodes和processor定义的节点都可以不写`iterator` 如可以写`web.gdelt.Export`
7. 支持获取环境变量，在consts中声明，如`api_key: $OPENAI_KEY` 表示从环境变量中读取OPENAI_KEY的值并赋给api_key
8. 对多个流程补充描述说明

- 2024.10.25
1. 修改GDLET数据加载器`GdeltTaskEmit` 调整睡眠模式 避免访问还未生成的zip文件
2. 新增`FieldConvert(key, converter)`算子，实现对指定字段进行类型转换，转换子为任意支持一个参数的函数 如`int` `float` `str` `bool`、`util.lang_util.zh_simple`等
3. 新增`Convert(converter)`算子，实现对记录的类型转换，转换子包括`int` `float` `str` `bool`等

- 2024.10.24
1. 新增GDELT处理流程，持续下载[查看](flows/gdelt.yaml) 滚动下载export.CSV.zip文件
2. 增加新的Loader `GdeltTaskEmit` 从指定时间开始下载数据并持续跟踪
3. 新增经济学人民调数据处理算子 `iterator.web.polls.PollData` （需要手工下载CSV）、处理流程[查看](flows/test_polls.yaml)
4. 修改`Flat`算子逻辑，如果输入为`dict`，则提取k-v，如果v也是`dict`，则把k填入v中（_key），最后输出v

- 2024.10.17
1. 添加多个处理算子：FieldJson、Flat、FlatMap、AddFields [查看](docs/iterator.md)
2. 初步添加规约类算子：BufferBase Reduce GroupBy

- 2024.10.15
1. 修改CkWriter参数为 username tcp_port 明确使用TCP端口（默认9000，而不是HTTP端口8123）
2. 新增字段值 String -> Json 算子 `FieldJson(key)`
3. 新增加载json文件到ClickHouse流程[查看](flows/db_import_mongo.yaml)
4. 新增ClickHouse表复制的流程[查看](flows/db_copy_clickhouse.yaml)

- 2024.10.14
1. 新增 MongoWriter
2. 新增 MongoDB表复制流程[查看](flows/db_copy_mongo.yaml)

- 2024.10.02
1. WriteJson WriterCSV增加编码参数设置
2. 新增GDELT本地数据处理的简化流程[查看](flows/test_gdelt.yaml) 通过加载本地文件转化成JSON

- 2024.09.30
1. 集成Reader API（`wikidata_filter.iterator.web.readerapi` 详见 https://jina.ai/reader/)
2. 增减文本文件加载器 TxtLoader（详见 `wikidata_filter.loader.file.TxtLoader`）
3. 新增Reader API的流程 [查看](flows/test_readerapi.yaml) 加载url列表文件 实现网页内容获取
