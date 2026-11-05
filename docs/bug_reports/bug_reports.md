### BUG-001
- 标题：[登录接口] 正确账号密码登录时 HTTP 返回 200，但响应 JSON 中 code=500，前端提示“系统错误”
- 严重程度：Critical
- 优先级：High
- 环境：Windows 11 / Apifox 2.x / 被测接口 http://127.0.0.1:8000/api/login / 后端 FastAPI（或 Mock 服务）
- 前置条件：
  1. 被测登录服务已启动，接口地址可访问。
  2. 系统中存在账号 admin，密码 123456，且账号状态正常。
- 复现步骤：
  1. 打开 Apifox，新建 POST 请求，URL 填 http://127.0.0.1:8000/api/login。
  2. Header 设置 Content-Type: application/json。
  3. Body 选择 JSON，填入 {"username":"admin","password":"123456"}。
  4. 点击发送，查看 HTTP 状态码和响应体。
- 预期结果：
  1. HTTP 状态码为 200。
  2. 响应 JSON 中 code=200，msg=success，data 中包含 token。
  3. 前端进入登录成功后的页面。
- 实际结果：
  1. HTTP 状态码为 200。
  2. 响应 JSON 中 code=500，msg 为“系统错误”或类似提示，data 为空，没有返回 token。
  3. 前端弹出“系统错误”，无法登录。
- 附件/证据：
  1. Apifox 请求与响应截图：请求体为 {"username":"admin","password":"123456"}，响应体为 {"code":500,"msg":"系统错误","data":null}。
  2. 后端日志中对应时间点有异常堆栈（如有则附上，没有则写“待补充”）。

### BUG-002
- 标题：[登录接口] 用户名为空时提交登录，返回500并暴露后端异常堆栈，而非400参数错误
- 严重程度：Critical
- 优先级：High
- 环境：Windows 11 / Apifox 2.x / 被测接口 http://127.0.0.1:8000/api/login / 后端 FastAPI（计划中或本地 Mock 服务）
- 前置条件：
  1. 被测登录服务已启动，接口地址可访问。
  2. 系统中存在密码为 123456 的测试账号，用于构造“用户名空、密码非空”的组合。
- 复现步骤：
  1. 打开 Apifox，新建 POST 请求，URL 填 http://127.0.0.1:8000/api/login。
  2. Header 设置 Content-Type: application/json。
  3. Body 选择 JSON，填入 {"username":"","password":"123456"}。
  4. 点击发送，查看 HTTP 状态码和响应体。
- 预期结果：
  1. HTTP 状态码为 400。
  2. 响应 JSON 中 code=400，msg 为“用户名不能为空”或类似明确提示。
  3. 不返回 token，不暴露任何后端堆栈或内部路径。
- 实际结果：
  1. HTTP 状态码为 500。
  2. 响应 JSON 中 code=500，msg 为“系统错误”，data 为空。
  3. 响应体或日志中出现后端异常堆栈（如 Traceback、文件路径、代码行号），存在信息泄露风险。
  4. 前端弹出“系统错误”，无法登录。
- 附件/证据：
  1. Apifox 请求与响应截图：请求体为 {"username":"","password":"123456"}，响应体为 {"code":500,"msg":"系统错误","data":null}。
  2. 后端日志/响应中的异常堆栈截图（如有则附，没有写“待补充”）。

### BUG-003
- 标题：[登录接口] 密码长度上限为20位，传入21位密码时仍返回登录成功，未触发长度超限校验
- 严重程度：Critical
- 优先级：High
- 环境：Windows 11 / Apifox 2.x / 被测接口 http://127.0.0.1:8000/api/login / 后端 FastAPI（计划中或本地 Mock 服务）
- 前置条件：
  1. 被测登录服务已启动，接口地址可访问。
  2. 系统中存在账号 admin，其密码为合法长度（如 123456）。
  3. 根据需求/接口文档，密码长度上限为 20 位。
- 复现步骤：
  1. 打开 Apifox，新建 POST 请求，URL 填 http://127.0.0.1:8000/api/login。
  2. Header 设置 Content-Type: application/json。
  3. Body 选择 JSON，填入 {"username":"admin","password":"aaaaaaaaaaaaaaaaaaaaa"}（21位）。
  4. 点击发送，查看 HTTP 状态码和响应体。
- 预期结果：
  1. HTTP 状态码为 400。
  2. 响应 JSON 中 code=400，msg 为“密码长度不能超过20位”或类似明确提示。
  3. 不返回 token。
- 实际结果：
  1. HTTP 状态码为 200。
  2. 响应 JSON 中 code=200，msg=success，data 中包含 token。
  3. 前端进入登录成功后的页面，未触发长度超限校验。
- 附件/证据：
  1. Apifox 请求与响应截图：请求体为 {"username":"admin","password":"aaaaaaaaaaaaaaaaaaaaa"}，响应体为 {"code":200,"msg":"success","data":{"token":"xxx"}}。
  2. 后端日志中对应时间点记录（如有则附，没有写“待补充”）。