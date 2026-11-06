# Mock后端接口说明

## 启动方式
在 PyCharm 中右键运行 `mock_server/main.py`，或终端执行 `uvicorn mock_server.main:app --reload`。
Swagger 文档地址：http://127.0.0.1:8000/docs

## 接口清单
| 方法 | 路径 | 鉴权 | 成功业务 code | 关键异常 |
|---|---|---|---|---|
| POST | /api/login | 无 | 200 (返回token) | 用户名/密码空、超长、不存在 → 业务 code 400 (HTTP 200) |
| GET | /api/user/{user_id} | Bearer Token | 200 (返回用户信息) | 无token/格式错/token无效 → HTTP 401；用户不存在 → HTTP 404 |
| PUT | /api/user/{user_id} | Bearer Token | 200 (返回新信息) | 同上 |
| DELETE | /api/user/{user_id} | Bearer Token | 200 | 同上 |

## 设计决策（面试重点）
1. **两层校验**：登录失败（业务错误）使用 HTTP 200 + 业务 code 400；鉴权失败使用 HTTP 401。自动化断言时需同时校验这两层。
2. **数据存储**：使用内存字典 `USERS`，重启即重置，保证测试数据可控、用例互不污染。
3. **依赖注入**：使用 `Depends` 和 `HTTPBearer` 实现接口级鉴权，清晰区分公开接口（login）和受保护接口（user相关）。