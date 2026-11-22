# 用例管理平台数据表设计（Day24）

本文档只做表设计，不写代码。代码见 `tools/case_store.py`。
数据库用 SQLite（文件即库，不装服务），SQL 语法和 MySQL 基本一致，方言差异见文末。

## 五张核心表

### 1. case_info（用例信息）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | 主键 |
| case_id | TEXT UNIQUE NOT NULL | 业务ID，如 login_001，人看的 |
| title | TEXT NOT NULL | 用例标题 |
| module | TEXT | 所属模块，如 登录/用户 |
| priority | TEXT DEFAULT 'P1' | P0/P1/P2 |
| precondition | TEXT | 前置条件（对应 Day22 用例表） |
| steps | TEXT | 操作步骤（对应 Day22 用例表） |
| expected | TEXT | 预期结果（对应 Day22 用例表） |
| yaml_path | TEXT | 对应的 yaml 文件路径 |
| enabled | INTEGER DEFAULT 1 | 1启用/0禁用 |
| created_at | TEXT | 创建时间 |

**关键点**：
- 两个 ID 都要：`id` 给数据库内部用（自增、稳定，其他表做外键），`case_id` 给人用（`login_001`，yaml 里也用它关联）。
- `precondition / steps / expected` 对应 Day22 手工用例表的核心列，不写进表则平台上的用例详情没内容可展示。
- `enabled` 是禁用不是删除：删了历史执行记录就找不到这条用例，禁用保留记录。

### 2. case_set（用例集）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | 主键 |
| set_name | TEXT UNIQUE NOT NULL | 集合名，如 smoke/full |
| description | TEXT | 说明 |

**关键点**：`smoke` 是每次提交都跑的少量核心用例，`full` 是发版前跑的全部用例。用例集是**执行单位**——你不会一条一条跑，你跑的是一个集合。

### 3. case_set_mapping（用例集和用例的关联）

| 字段 | 类型 | 说明 |
|---|---|---|
| set_id | INTEGER FK | 关联 case_set.id |
| case_info_id | INTEGER FK | 关联 case_info.id |
| （联合主键） | PRIMARY KEY (set_id, case_info_id) | 防止重复关联 |

**关键点**：一个用例可以属于多个集合（`login_001` 既在 smoke 也在 full），这是**多对多**关系，需要中间表。不用中间表的两种错法：在 `case_info` 加 `set_name` 存 `"smoke,full"` 字符串（查询要 LIKE、没法建索引、会误匹配）；或复制两条记录（改标题要改两处，容易不一致）。

### 4. execution（执行记录）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | 主键 |
| set_id | INTEGER FK | 本次执行哪个用例集 |
| env | TEXT | dev/test |
| started_at | TEXT | 开始时间 |
| finished_at | TEXT | 结束时间 |
| total | INTEGER DEFAULT 0 | 总用例数 |
| passed | INTEGER DEFAULT 0 | 通过数 |
| failed | INTEGER DEFAULT 0 | 失败数 |

**关键点**：这张表存"一次执行"的**汇总**，不存每条用例的结果。`total/passed/failed` 是冗余字段——写入时从明细汇总算好，查"历史通过率趋势"时直接读，不用每次 COUNT。

### 5. execution_detail（执行明细）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | 主键 |
| execution_id | INTEGER FK | 关联 execution.id |
| case_info_id | INTEGER FK | 关联 case_info.id |
| case_id | TEXT | 冗余的业务 ID，查询少一层 JOIN |
| status | TEXT | passed/failed/skipped |
| error_msg | TEXT | 失败原因 |
| duration_ms | INTEGER | 耗时 |

**关键点**：**这张表是今天的核心。** 每跑一条用例写一条明细，**绝不在 `case_info` 上直接改 `status`**——改了就只剩最后一次状态，历史全丢。`case_id` 冗余字段是为了查失败用例时少一层 JOIN，且业务 ID 比自增主键可读。

## 五张表的关系
```text 
case_info（用例）
↑ 多对多，通过 case_set_mapping
case_set（用例集）
↓ 一对多
execution（一次执行）
↓ 一对多
execution_detail（每条用例的结果）──→ case_info（这条明细对应哪条用例）
```
