# 设计

## 项目需求
1. 对wikidata、wikipedia等数据进行预处理，方便业务系统使用
2. 不同业务系统处理需求各异，处理流程（pipeline/flow）需要灵活可配
3. 支持从文件、常用数据库进行读取和写入

## 核心概念
- Flow: 处理流程，实现数据载入（或生成）、处理、输出的过程
- Loader：数据加载节点（对应flume的`source`） 
- Iterator：数据处理节点，用于表示各种各样的处理逻辑，包括数据输出与写入数据库（对应flume的`sink`）  
- Matcher：数据匹配节点，是一类特殊的`Iterator`，可作为函数调用
- Engine：按照Flow的定义进行执行。简单Engine只支持单线程执行。高级Engine支持并发执行，并发机制通用有多线程、多进程等


## 总体设计
### Loader设计
【输入】从各类数据源加载数据，以单条或多条在流程节点中进行流转。适配常见的文件、数据库等。
1. 基类`DataLoader`，定义基础Loader接口，可作为函数调用
2. 文件加载器`FileLoader`，支持多种可产生列表数据的文件，包括JSON、CSV等
3. 数据生成器，`RandomGenerator`生成指定数量的伪随机数（0~1）
4. wikidata：支持全量Dump文件（JSON/JSON-gz/JSON-bz2）、支持增量文件（XML/XML-bz2）
5. 数据库：支持ElasticSearch、ClickHouse、MongoDB

### Iterator设计
【计算+输出】将常见数据处理过程抽象、拆分为多个处理算子，通过处理算子的组合形成处理流程。结果输出也是一种数据处理算子，包括输出到文件、输出到数据库等。
1. 基类`JsonIterator`，定义基础Iterator接口
2. 基础操作：`Filter`、`Print`、`Count`、`Repeat`、`Buffer`
3. 修改操作：`Select`、`Map`、`RemoveFields` `RenameFields` `FillField` `CopyFields` `UpdateFields`
4. wikidata处理：`IDNameMap` `Simplify` `SimplifyProps` `PropsFilter` `ValuesFilter` `ObjectNameInject` `ItemAbstractInject` `ChineseSimple` `AsRelation`
5. wikipedia处理：`ToHTML` `PageAbstract`
6. 输出文件：`WriteJson` `WriteCSV`
7. 输出到数据库：支持ElasticSearch `ESWriter`、ClickHouse `CKWriter`
8. 匹配节点：`SimpleJsonMatcher` `JsonPathMatcher` `WikidataMatcher`
9. 组合节点：并行`Group`、串行`Chain`

未来可以支持更加复杂的算子，比如汇合（Join）

### Flow设计
- Raw Flow：基于python的流程组装，通过`wikidata_*`提供了一套wikidata处理流程
- YAML Flow：基于YAML文件定义处理流程 参考[可配置流程设计](yaml-flow-design.md)

### Engine设计

**TODO**


## 下一步计划
1. 与`python-streaming`等历史项目进行整合（多种文件解析、知识图谱的构建生成） 更加更多组件
2. 引擎支持并行化处理，提高处理性能
