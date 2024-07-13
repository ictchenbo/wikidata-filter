## 处理节点（Iterator）

模块：`wikidata_filter.iterator`


### 基类设计
1. 抽象基类 `JsonIterator` 定义了数据处理的接口
2. 


### 基础类
1. 打印数据 `Print` 方便调试或日志记录 无参数
2. 计数 `Count` 对数据进行统计，方便观察 参数：ticks、label
3. 过滤 `Filter` 参数：过滤函数/Matcher对象
4. 缓冲 `Buffer` 参数：


### 修改类
1. 投影操作 `Select`
2. 数据映射转换 `Map`
3. 移除字段 `RemoveFields`
4. 重命名字段 `RenameFields`
5. 字段拷贝 `CopyFields`
6. 字段更新 `UpdateFields`
7. 字段填充 `FillFields`


### 输出文件
1. JSON文件 `WriteJSON`
2. CSV文件 `WriteCSV`


### 输出到数据库
1. ElasticSearch 
2. ClickHouse


### 组合节点
1. 并行处理 `Group`
2. 串行处理 `Chain`
3. 重复数据 `Repeat`
