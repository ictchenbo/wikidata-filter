create table if not exists item (id String, modified String, name String, name_en String, desc String, desc_en String, aliases Array(String)) engine=MergeTree order by toUInt64OrZero(substring(id, 2));

create table if not exists property (id String, modified String, name String, name_en String, desc String, desc_en String, aliases Array(String)) engine=MergeTree order by toUInt64OrZero(substring(id, 2));

create table if not exists item_property (id String, qid String, pid String, datatype String, datavalue String) engine=MergeTree order by toUInt64OrZero(substring(qid, 2));

create table if not exists property_property (id String, pid String, datatype String, datavalue String) engine=MergeTree order by id;
