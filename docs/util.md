## 辅助工具

模块：`wikidata_filter.util`

构造器：`util.<Comp>(*args, **kwargs)`

### 加载集合数据
1. `util.SetFromCSV(filename, index=0)`
2. `util.SetFromJSON(filename, key_key='id')`
3. `util.KVFromCSV(filename, key_col=0, val_col=1)`
4. `util.KVFromJSON(filename, key_key='id', val_key='name')`

### JSON操作工具
1. 提取JSON对象的值 `util.json_op.extract_val(val, path)`
2. 设置JSON对象的值 `util.json_op.fill_val(val, path, value)`

### 语言工具
1. 转为中文简体 `util.lang_util.zh_simple(s)`

### 文件
1. 读取文本文件内容 `util.files.read_text(filename, encoding='utf8')`

### 日期时间
1. 当前时间（1970.1.1以来的秒） `util.dates.current()`
2. 当前时间（1970.1.1以来的毫秒） `util.dates.current_ts()`
3. 当前日期（形式：2024-11-01） `util.dates.current_date(fmt='%Y-%m-%d')`
4. 当前时间（形式：2024-11-01 15:50:00） `util.dates.current_time(fmt='%Y-%m-%d %H:%M:%S')`
5. 字符串日期转时间戳（1970.1.1以来的秒） `util.dates.date(date, fmt='%Y-%m-%d')`
6. 字符串日期转时间戳（1970.1.1以来的毫秒） `util.dates.date_ts(date,fmt='%Y-%m-%d')`
7. 日期格式化 `util.dates.ts2date(ts, fmt='%Y-%m-%d')` 输入为秒
8. 时间格式化 `util.dates.ts2datetime(ts, fmt='%Y-%m-%d')` 输入为秒

