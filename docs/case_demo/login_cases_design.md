# 登录接口自动化用例设计说明

## 1. 文档目的

记录登录接口从“手工用例”到“yaml数据驱动+三层断言”的设计过程。
面试时可打开本文档，说明：
- 用例为什么是这8条，覆盖了哪些等价类和边界值；
- yaml字段为什么这样设计；
- 断言为什么分三层，而不是只断言HTTP 200；
- 新增接口时，为什么只改yaml和test脚本，不改common。

## 2. 被测接口

- 方法：POST
- 路径：/api/login
- 请求体：`{"username": "xxx", "password": "xxx"}`
- 成功：HTTP 200，业务 `code=200`，`data.token` 非空
- 失败：HTTP 200 + 业务 `code=400`（参数/业务校验失败）
- 框架层校验失败：HTTP 422（缺少必填字段，Pydantic拦截，无业务code）

## 3. 用例设计依据

### 3.1 等价类划分

| 等价类 | 有效/无效 | 对应用例 |
|---|---|---|
| 正确账号密码 | 有效 | login_001 |
| 用户名为空 | 无效 | login_002 |
| 密码为空 | 无效 | login_003 |
| 缺少username字段 | 无效（框架层） | login_004 |
| 账号不存在 | 无效 | login_007 |
| 密码错误 | 无效 | login_008 |

### 3.2 边界值分析

密码长度假设上限为20：

| 边界点 | 取值 | 对应用例 | 预期 |
|---|---|---|---|
| 边界内 | 20位 | login_005 | 不触发长度校验，返回“账号或密码错误” |
| 边界外（上点+1） | 21位 | login_006 | 触发长度校验，返回“密码长度过长” |

### 3.3 特殊场景

- **login_004（缺少username）**：FastAPI的Pydantic在进入业务函数前返回HTTP 422，响应体为`{"detail": [...]}`，无业务`code`字段。这条用例的预期是`expect_http: 422`、`expect_code: null`，脚本跳过业务code断言。这验证的是“框架层校验”和“业务层校验”是两层，不能混为一谈。

## 4. yaml用例结构设计

每条用例的字段：

| 字段 | 含义 | 是否必填 |
|---|---|---|
| case_id | 用例唯一ID，用于报告和失败定位 | 是 |
| title | 用例标题 | 是 |
| method | HTTP方法 | 是 |
| path | 接口路径 | 是 |
| json | 请求体 | 否（GET可不传） |
| expect_http | 预期HTTP状态码 | 是 |
| expect_code | 预期业务code | 否（422时为null） |
| expect_msg | 预期msg包含的子串 | 否 |
| expect_fields | 预期响应结构中必须存在的字段路径列表 | 否 |
| smoke | 是否冒烟用例 | 否 |

设计原则：
- yaml顶层是**列表**，每条用例以 `- case_id` 开头，`read_yaml` 读出来直接是`list[dict]`，可直接传给`parametrize`。
- 字段命名统一，后续新增接口沿用同一骨架，不重新发明字段。
- `expect_msg`用**子串包含**断言，不是完全相等，容忍文案的细微变化。
- `expect_fields`用**路径列表**，支持嵌套结构，如`data.token`。

## 5. 三层断言设计

### 5.1 HTTP状态码断言

```python
assert resp.status_code == case["expect_http"]
```
防的是：后端路由错误、服务不可用、框架层校验失败（422）等协议层问题。

### 5.2 业务code断言
```python
if case.get("expect_code") is not None:
    body = resp.json()
    assert body["code"] == case["expect_code"]
```
防的是：HTTP 200但业务失败（如空密码、账号不存在）。login_004的expect_code为null，跳过此断言。

### 5.3 结构断言
```python
if case.get("expect_fields"):
    _assert_fields_exist(body, case["expect_fields"], case["case_id"])
```
防的是：字段被改名、被删除、值为null。比如后端把data.token改成data.access_token，值断言可能仍通过，但结构断言会失败。

_assert_fields_exist的设计：

- payload：响应体字典，作为路径起点；

- field_paths：路径列表，如["data.token"]；

- case_id：仅用于失败消息定位；

- current = payload：每条路径从原始payload重新走，避免多路径时起点被覆盖。

## 6. 失败信息设计
每条断言都带f-string消息，包含：
- case_id
- 期望值
- 实际值
- 完整body

示例：

```text
[login_006] msg不符: 期望包含'密码长度过长', 实际'密码长度过长，最大为20'
```
目的：CI跑失败时，不看代码、不翻日志，仅凭失败消息就能定位是哪条用例、哪个字段、期望什么、实际什么。

## 7. 遇到的问题与处理
### 7.1 login_006的msg预期不一致 
yaml最初写expect_msg: 密码过长，后端实际返回密码长度过长，最大为20。"密码过长"不是后者的子串，断言失败。

处理：将yaml预期改为密码长度过长，对齐后端真实且合理的文案。不改后端迁就测试，也不放宽断言。

### 7.2 login_004的HTTP 422与业务code
缺少username时，FastAPI返回HTTP 422，响应体无code字段。yaml中expect_code: null，脚本用if case.get("expect_code") is not None跳过业务code断言。这不是漏测，是承认框架层校验先于业务层执行。

## 8. 解耦验证
新增GET /api/user/{user_id}接口时：

- 新增：cases/get_user_case.yaml、test_cases/test_get_user.py

- 不改：common/request_util.py、common/yaml_util.py、conftest.py

request_util.send(method, path, **kwargs)不关心具体接口，只负责发请求、记日志、抛异常。新增接口不需要动底层封装，这是分层解耦的验收标准