## 可配置流程设计
**动机**：通过简易配置，实现处理流程灵活可配

**目标**：替代现有wikidata_p*等py主文件，便于修改配置

**需求设计**
1. 流程以yaml格式进行定义
2. 支持流程名称及描述定义
3. 支持数据加载器组件定义，对应 `wikidata_filter.loader`
4. 支持数据处理器组件定义，对应 `wikidata_filter.iterator`
5. 组件定义为 key-value 形式，其中key为该组件在流程中的唯一标识，便于其他组件引用；value为组件构造器
6. 组件构造器即组件类的构造语句，完整形式为 `<Component>(arg1*) `；如果构造器的参数为空，可简写为`<Component>`
7. 构造器参数：
 - 常见Python值，字符串（引号包裹）、数字、bool（`True`/`False`）、None、字典（`{}`）、数组（`[]`）、对象（`Cls()`）
 - 其他组件：通过key引用流程定义的其他组件
 - 环境变量：流程命令行参数（arg1, arg2 ...）、环境变量（__var） （遗憾！python的变量名不支持`$`）

### 流程组件
1. `consts` 在这个下面定义的yaml数据（字符串、数值、数组、字典）可以被其他组件构造器使用
2. `loader` 定义数据加载器组件 **有且仅有一个**
3. `nodes` 定义流程处理器节点 可定义0个或者多个
4. `processor` 定义流程处理器 **有且仅有一个**

其中`nodes`中python表达式的执行，其值为对应表达式的执行结果。在yaml中以=开头，例如：
```yaml
nodes:
  id_set: util.SetFromCSV('data/entity_id.csv')
  matcher: "=lambda item: item.get('mongo_id') not in id_set"
```
这里定义了两个节点：id_set和matcher，其中id_set为基于文件构造的集合，matcher定义为一个lamda函数

### 运行参数
通过`arguments` 指定流程需要几个运行参数，在组件中分别用 `arg1` `arg2` ... 引用
