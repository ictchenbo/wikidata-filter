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