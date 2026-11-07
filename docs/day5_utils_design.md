# Day5 工具层设计说明

## 1. 分层结构
- common/：工具层，只负责“怎么发请求、怎么读配置、怎么打日志”，不含任何业务用例。
- config/：配置层，环境地址与代码分离。
- conftest.py：pytest 全局夹具，负责创建 client 和登录获取 token。

## 2. 关键设计决策

### 为什么用 requests.Session 而不是 requests.post()
- Session 能跨请求保持 headers 和 Cookie。
- token 通过 session.headers.update() 写入后，后续所有请求自动携带，用例不需要手动传 Authorization。

### 为什么 login_token 的 scope 是 session
- 整个测试会话只登录一次，避免每个用例重复登录。
- 如果改成 function，用例越多登录次数越多，浪费时间且可能触发后端登录频率限制。

### 为什么 yaml 用 safe_load
- safe_load 只解析标准 YAML 类型，不会执行任意 Python 对象。
- load 有安全风险，项目内禁止使用。

### 为什么 request_util 捕获异常后还要 raise
- 捕获是为了记录精确的失败原因到日志。
- raise 是为了让 pytest 仍然把用例标记为失败，不吞掉异常。

### 为什么登录 fixture 里先断言 HTTP 200 再断言业务 code 200
- HTTP 200 只代表请求到达了后端，不代表业务成功。
- 两层断言缺一不可，对应 Day3 BUG-001 的场景。

## 3. 多环境切换方式
- 修改 config/env.yaml 中的 current_env 为 dev 或 test，代码零改动。
