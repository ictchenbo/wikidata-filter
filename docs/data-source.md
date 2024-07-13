****# 数据资源库设计

**动机** 形成各类基础数据资源库，提供数据统一管理并支撑应用系统查询、使用

**目标**
1. 覆盖大GoIN主要数据资源需求
2. 数据类型支持：结构化数据（单表、多表、图谱）和非结构化数据（各类文档、压缩包）
3. 数据接入：支持文件上传、数据库导入等常见接入方式
4. 数据使用：提供数据检索、统计和导出

## 功能设计
1. 数据预处理：以算子插件形式，支持灵活的预处理流程；内置wikidata、wikipedia、GDELT等数据预处理算子
2. 内置多种预处理算子：包括文件加载器、筛选、格式转换、输出等
3. 处理流程可配置：基于配置方式，以并行或串行方式组合多个预处理算子
4. 统一存储：对各类数据进行统一存储
5. 检索与统计：提供简单接口对数据进行检索、统计与查看
6. 数据导出：生成导出文件或提供数据读取接口

## 业务逻辑设计
1. 一个数据资源包含


## 数据资源建设
1. 定期更新类：wikidata、wikipedia、GTD
2. 持续更新类：GDELT

## 存储设计
以文件进行存储

## 元数据设计
1. 元数据库 MongoDB resource表
- _id 资源ID
- name 资源名称
- tags 标签
- desc 描述
- directory 文件夹路径（相对于系统存储的根路径 根路径为全局配置） 下面包含1个或多个文件
- owner 属主
- create_time 创建时间
- update_time 更新时间****

2. 文件 file表
- _id 
- resource_id
- name 文件名称
- desc 文件描述
- path 相对于资源文件夹的文件路径
- metadata 文件元数据 作者、创建日期、修改日期、标签等

3. 结构化文件信息结构 schema表
- _id
- file_id
- name 字段名称
- type 字段类型
- desc 字段描述

4. 结构化文件引用关系 reference表
- _id
- file_id
- main 当前文件的外引字段名称（`files[i].schemas[j].name`）
- references 被引用的外部文件列表
- references[k].file 被引用的外部文件名（`files[r].name`）
- references[k].key 被引用的外部文件的字段（`files[r].schemas[s].name`） 不支持再次引用或循环引用

5. 索引管理 index表
- _id
- file_id 
- key 索引字段 `files[r].schemas[s].name`
- type 索引类型 

