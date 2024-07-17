## 数据加载器（Loader）

模块：`wikidata_filter.loader`

构造器：`<Comp>(*args, **kwargs)` 或 `<module>.<Comp>(*args, **kwargs)`

### 基类设计
1. 抽象基类 `DataLoader` 定义了数据加载器的接口
2. 抽象基类 `FileLoader` 文件数据加载器

### 文件加载器
1. 按行读取文件 `LineBasedFileLoader` 每行为原始字符串。不建议使用
2. JSON行文件 `JsonLineFileLoader` 每行按照JSON进行解析，以字典`dict`结构进行传递。
3. JSON数组文件 `JsonArrayLoader` 整个文件为一个JSON数组，依次传递数组中的每个元素。
4. CSV文件 `CSVLoader` 按照CSV文件进行解析，如果带有表头，则以字典结构进行传递，否则以单元格列表进行传递。


### wikidata文件
提供两种wikidata文件格式加载器：
1. 全量dump文件：`wikidata.WikidataJsonDump` 本质上是一个每行一项的JSON数组文件 
2. 增量文件：`wikidata.WikidataXmlIncr` 本质上是wiki修订记录的XML文件的合并（即一个文件中包含了多个完整XML结构）


**说明**：
上述文件都支持以gz或bz2进行压缩，根据文件后缀名进行判断（分别为`.gz`和`.bz2`）

**实例化参数**：文件路径；编码（默认为utf8）


### 数据库加载器
提供常用数据库的数据查询式读取：
1. ClickHouse `database.CKLoader` 实例化参数：
- host 服务器主机名 默认`"localhost"`
- port 服务器端口号 默认 `9000`
- user 用户名 默认`"default"`
- password 密码 默认`""`
- database 数据库 默认`"default"`
- table 表名 无默认值必须指定
- select 返回字段 默认`"*"` 示例`"id,name"`
- where 过滤条件 默认`None` 示例`a = '123' AND b is NULL` 
- limit 限制条件 默认`None` 示例`10,20`（即跳过10条返回20条）

示例配置：
```python
database.CKLoader(host='10.208.57.5', port=59000, database='goin_kjqb_230202_v_3_0', table='entity_share_data_shard', select='mongo_id, name')
```

2. ElasticSearch `database.ESLoader` 实例化参数：
- host 服务器主机名 默认`"localhost"`
- port 服务器端口号 默认 `9200`
- user 用户名 默认`None`
- password 密码 默认`None`
- table 索引名 无默认值
- select 返回字段 默认`"*"` 示例`"id,name"`
- where 查询条件（参考[ES查询语法](http://)) 默认为`None`表示全部
- limit 限制数量（整数）

**注意**：由于ES常规检索方式限制最多返回10000条数据，因此limit>10000时采用scroll API。请参考：

示例配置：
```python
database.ESLoader(host='10.208.57.13', table='docs')
```

3. MongoDB `MongoLoader` 实例化参数：
- host 服务器主机名 默认`"localhost"`
- port 服务器端口号 默认 `27017`
- username 用户名 默认`None`
- password 密码 默认`None`
- auth_db 认证数据库 默认`"admin"`
- database 数据库 默认`"default"`
- table 表名 无默认值必须指定
- select 返回字段 默认`"*"` 示例`"id,name"`
- where 查询条件（参考）默认为`None`表示全部，示例`{"name": "abc"}` 
- limit 限制数量（整数）

示例配置：
```python
database.MongoLoader(host='10.208.57.13', table='nodes')
```


### 其他加载器

1. 随机数生成器 `RandomGenerator`
