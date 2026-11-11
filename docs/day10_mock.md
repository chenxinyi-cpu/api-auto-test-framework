# Mock 在接口自动化中的两层含义与适用边界

## 一、两层 Mock 的区别

### 1. 服务级 Mock（mock_server/ 下的 FastAPI 后端）

- **做法**：用 FastAPI 真实启动一个 HTTP 服务，监听 127.0.0.1:8000。
- **特点**：走真实网络，有真实 HTTP 层，能测 401（无 token）、422（路径参数类型错误）、业务 code 400（空参数）等真实行为。
- **在项目中的位置**：作为项目A的被测系统（SUT），主回归用例（test_login.py、test_get_user.py）全部打这个后端。
- **适合场景**：验证“被测对象自己的业务逻辑”，包括参数校验、鉴权、路径参数、业务状态码。

### 2. 代码级 Mock（test_cases/test_mock_demo.py，使用 responses）

- **做法**：用 `@responses.activate` 在 `requests` 发起网络请求之前拦截，直接返回预设响应。
- **特点**：不发出真实网络请求，后端在不在都能跑；速度快、隔离性好、可控性强。
- **在项目中的位置**：独立演示文件，不进入主回归，只证明“会隔离下游依赖”。
- **适合场景**：验证“客户端拿到特定响应后怎么处理”，包括响应解析、token 注入、异常抛出。

### 一句话区分

- 服务级 Mock 回答：**服务端收到这个请求后应该怎么处理？**
- 代码级 Mock 回答：**客户端收到这个响应后应该怎么处理？**

---

## 二、什么时候该 Mock

1. **下游服务不稳定或不可用**：第三方支付、短信网关、外部 LLM API，真实调用会限流、收费、偶发超时。
2. **异常场景难以真实触发**：连接断开、请求超时、服务端 500，靠真实环境很难稳定复现。
3. **单元测试中替换非确定性依赖**：当前时间、随机数、数据库连接函数（这类用 pytest-mock 的 mocker.patch 更合适，不是 responses）。

## 三、什么时候不该 Mock

1. **被测对象自身的核心逻辑**：登录参数校验、token 鉴权、路径参数类型校验。Mock 掉它们，401、422、业务 code 400 全部测不到，测试变成“自己骗自己”。
2. **联调验证**：必须用真实后端跑一遍。Mock 测试通过 ≠ 系统集成正确。
3. **真实接口契约可能变化的场景**：Mock 不会告诉你字段改名了。后端把 `token` 改成 `access_token`，Mock 测试照样绿，联调直接挂。

---

## 四、项目A里的取舍

- **主回归用真实 FastAPI 后端**：`test_login.py`（8条）、`test_get_user.py`（4条带token + 1条无token），全部打真实后端，保证集成正确。
- **`test_mock_demo.py` 只做能力演示**：三个用例分别验证
  1. `test_first_mock`：GET 响应被正确解析，`responses.calls` 证明请求确实发出。
  2. `test_login_mock`：POST 请求体被正确序列化（`json.loads(request.body)` 后按字段断言）。
  3. `test_login_connection_error_with_mocked_backend`：`request_util` 的 `raise` 不是摆设。
- **CI 里跑的是真实后端**：`.github/workflows/pytest-ci.yml` 后台启动 `mock_server/main.py`，健康检查通过后执行 `pytest -m smoke`。
- **`test_mock_demo.py` 在 CI 里也能跑**：因为它不依赖真实后端，`responses` 拦截后直接返回，不受后端启动影响。

---

## 五、亲手验证的结论（面试素材）

### 结论1：Mock 不检查请求体，只匹配 method + URL

`responses.add` 的 `json` 参数是“固定台词”，不是“业务逻辑”。

- 把 `test_login_mock` 的请求体从 `{"username":"admin","password":"123456"}` 改成 `{"username":"admin","password":"wrong_pwd"}`，测试**仍然 PASSED**。
- 因为 `responses` 只检查“方法是不是 POST、URL 是不是完全匹配”，不读 body 里的内容。
- **所以 Mock 测的是“客户端拿到响应后怎么办”，不是“服务端收到请求后怎么办”。**

### 结论2：`except` 里不 `raise`，测试会红，且报错形式比想象中更隐蔽

- 把 `common/request_util.py` 里 `except ConnectionError` 下的 `raise` 注释掉，跑 `test_login_connection_error_with_mocked_backend`。
- 测试失败，但报错**不是** `DID NOT RAISE ConnectionError`，而是 `UnboundLocalError: local variable 'resp' referenced before assignment`。
- 原因：异常被 `except` 吞掉后，代码继续往下执行，`resp` 因为请求失败从未被赋值，下一行 `resp.status_code` 直接炸在更远的地方。
- **说明**：吞异常不是让错误消失，而是让错误换一个更难排查的位置出现。`raise` 不是可有可无的装饰，它是让调用方知道失败的唯一途径。

### 结论3：Mock 测试通过 ≠ 系统集成正确

- 假设后端把登录失败响应从 `{"code": 400}` 改成 `{"code": 401}`，Mock 测试照样通过，因为 Mock 里写死了 `{"code": 400}`。
- 只有真实后端联调才能发现契约变化。
- **主回归必须用真实后端，Mock 只用于隔离下游依赖和验证客户端行为。**

---

## 六、responses 和 pytest-mock 的分工

| 工具 | 拦截/替换的对象 | 适用场景 |
|---|---|---|
| `responses` | `requests` 发出的 HTTP 请求 | Mock 下游 HTTP 依赖（第三方 API、微服务） |
| `pytest-mock` 的 `mocker.patch` | 任意 Python 函数/对象 | Mock 时间、随机数、数据库连接、内部函数 |

**项目A当前只用 `responses`**，因为演示的场景是“客户端发 HTTP 请求给下游”。如果后续需要 Mock “当前时间”或“数据库连接”，再用 `pytest-mock`。