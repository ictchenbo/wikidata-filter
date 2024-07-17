# wikidata-filter
Wikidata与Wikipedia数据处理框架，提供Wikidata&Wikipedia Dump数据解析、转换处理、文件加载、数据库加载、文件输出、数据库输出等。

关于wikidata知识图谱的介绍，可以参考作者的一篇博客文章 https://blog.csdn.net/weixin_40338859/article/details/120571090

## 项目特色
1. 通过`yaml`格式定义流程，上手容易
2. 内置数十种ETL算子，配置简单
3. 支持常见数据库的读取和写入
4. 内置wikidata和wikipedia处理流程，直接可用

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
简单示例：生成100个随机数并重复5遍 `flows/test_multiple.yaml`
```yaml
name: test multiple
nodes:
  n1: Repeat(5)
  n2: Count(ticks=5, label='Repeat')
  n3: Print

loader: RandomGenerator(100)
processor: Group(n1, n2, n3)

```

wikidata数据处理示例：对wikidata Dump文件生成id-name映射文件并简化数据结构 `flows/p1_idname_simple.yaml`
```yaml
name: p1_idname_simple
description:
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

3. 启动流程
**示例一**
```shell
 python main_flow.py flows/test_multiple.yaml
```

**示例二**
```shell
 python main_flow.py flows/p1_idname_simple.yaml dump.json simple.json
```

## 参考文档

YAML Flow [Flow 格式说明](docs/yaml-flow.md)

数据加载器 [Loader 说明文档](docs/loader.md)

处理节点（过滤、转换、输出等） [Iterator 说明文档](docs/iterator.md)

辅助函数 [util 说明文档](docs/util.md)


## 更多信息

详细设计说明[设计文档](docs/main-design.md)

Flow流程配置设计[可配置流程设计](docs/yaml-flow-design.md)
