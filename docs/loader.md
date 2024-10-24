## 数据加载器（Loader）

模块：`wikidata_filter.loader`

构造器：`<Comp>(*args, **kwargs)` 或 `<module>.<Comp>(*args, **kwargs)`

### 基类设计
1. 抽象基类 `DataLoader` 定义了数据加载器的接口
2. 抽象基类 `FileLoader` 文件数据加载器

### 文件加载器
1. 按行读取文本文件 `TxtLoader(input_file, encoding="utf8")` 每行为字符串
2. JSON行文件 `JsonLineFileLoader(input_file, encoding="utf8")` 每行按照JSON进行解析，以字典`dict`结构进行传递。
3. JSON数组文件 `JsonArrayLoader(input_file, encoding="utf8")` 整个文件为一个JSON数组，依次传递数组中的每个元素。
4. CSV文件 `CSVLoader(input_file, sep: str = ',', with_header: bool = False, encoding='utf8')` 按照CSV文件进行解析，如果带有表头，则以字典结构进行传递，否则以单元格列表进行传递。
5. Excel文件流式 `ExcelLoaderStream(input_file, sheets, with_header)`
6. Excel文件全量 `ExcelLoader(input_file, sheets, with_header)`


### wikidata文件
提供两种wikidata文件格式加载器：
1. 全量dump文件：`wikidata.WikidataJsonDump` 本质上是一个每行一项的JSON数组文件 
2. 增量文件：`wikidata.WikidataXmlIncr` 本质上是wiki修订记录的XML文件的合并（即一个文件中包含了多个完整XML结构）

**说明**：
- 上述文件都支持以gz或bz2进行压缩，根据文件后缀名进行判断（分别为`.gz`和`.bz2`）
- wikidata Dump文件下载地址：https://dumps.wikimedia.org/wikidatawiki/entities/

**实例化参数**：文件路径；编码（默认为utf8）

### GDELT数据
提供GDELT数据加载（通过网络下载） 每行提供url、file_size信息 配合对应iterator
1. 最近15分钟更新记录 `web.gdelt.GdeltLatest` 下载地址：http://data.gdeltproject.org/gdeltv2/lastupdate.txt
2. 全部文件，自2015年2月19日以来的全部更新记录 `web.gdelt.GdeltAll` 下载地址：http://data.gdeltproject.org/gdeltv2/masterfilelist.txt
3. 从指定某个时间开始历史记录 `web.gdelt.GdeltTaskEmit(2024, 9, 1)` 自动保存最新时间戳 程序重启后可以从之前的点恢复


### GTD（全球恐怖主义事件库）
GTD文件为Excel，通过`ExcelLoaderStream` 进行加载，可参考`flows/gtd_test.yaml`


### 数据库加载器
提供常用数据库的数据查询式读取：
1. ClickHouse `database.CKLoader` 实例化参数：
- host 服务器主机名 默认`"localhost"`
- tcp_port 服务器端口号 默认 `9000`
- username 用户名 默认`"default"`
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

4. MySQL `MySQLLoader` 参数同ClickHouse
5. PostgresSQL `PostgresSQLLoader` 参数同ClickHouse

### 其他加载器

1. 随机数生成器 `RandomGenerator`
