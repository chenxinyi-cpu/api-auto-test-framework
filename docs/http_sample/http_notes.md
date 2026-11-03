# HTTP接口基础笔记

## 1. HTTP请求报文
- 请求行：方法 + 路径 + 协议版本。例如 `POST /api/login HTTP/1.1`
- 请求头：附加说明，键值对。常见有 `Content-Type`、`Authorization`、`Accept`
- 请求体：真正传给后端的数据。GET 通常没有，POST/PUT 常用 JSON

## 2. HTTP响应报文
- 状态行：协议版本 + 状态码 + 状态描述。例如 HTTP/1.1 200 OK
- 响应头：附加说明。重点看 Content-Type，判断响应体是 JSON 还是 HTML
- 响应体：服务器返回的数据。接口测试主要断言这里


## 3. GET和POST区别
- GET：一般用于查询。参数常放 URL query，通常没有请求体。成功返回 200。
- POST：一般用于提交/创建。参数常放请求体，用 Content-Type: application/json 声明 JSON。创建成功常见 201。

## 4. 常见状态码
- 200：请求成功，响应体有数据。
- 201：创建成功，常见于 POST 新增资源。
- 400：请求参数错误，比如必填项为空、格式不对。
- 401：未认证。没带 token、token 过期或错误。
- 403：已认证但无权限。登录了，但不让访问该资源。
- 404：服务器找不到请求的资源，常见 URL 路径错误。
- 500：服务端内部错误，后端代码或依赖出问题。

## 5. 401和403区别
- 401：你是谁没验证。没带凭证、token 失效、token 错误。
- 403：知道你是谁，但你不配。身份验证通过，权限不够。

## 7. Token鉴权
- 客户端登录成功后，服务端返回一个 token。后续请求在请求头携带：Authorization: Bearer {token}
- Authorization格式：
1. Authorization：HTTP 认证请求头 
2. Bearer：认证方案，表示持有 token 即可访问 
3. {token}：登录后服务端返回的凭证

