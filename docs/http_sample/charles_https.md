# Charles HTTPS 抓包与断点调试记录

## 一、 为什么需要配置 Charles 抓 HTTPS？
HTTP 协议是明文传输，而 HTTPS 是加密传输。Charles 要想查看 HTTPS 的请求体和响应体，必须充当“中间人”（Man-in-the-Middle）：
1. 客户端向 Charles 发送请求。
2. Charles 伪造证书与客户端通信，并截获数据。
3. Charles 再与真实的服务器通信。
因此，客户端必须**信任** Charles 伪造的根证书，否则无法解密。

## 二、 核心配置步骤
1. **安装并信任证书**：
   - 菜单栏 `Help` -> `SSL Proxying` -> `Install Charles Root Certificate`。
   - Windows 系统需将其导入到“**受信任的根证书颁发机构**”；Mac 系统需在钥匙串中设置为“**始终信任**”。
2. **开启 SSL Proxying**：
   - 菜单栏 `Proxy` -> `SSL Proxying Settings` -> 勾选 `Enable SSL Proxying`。
   - 添加需要解密的域名，如 `*:443` 或指定域名如 `postman-echo.com:443`。
3. **确保客户端流量经过代理**：
   - 确保系统代理已开启（Charles 菜单栏 `Proxy` -> `macOS Proxy` / `Windows Proxy`）。
   - 确保 Apifox 等工具使用“系统代理”或在工具内配置了 `127.0.0.1:8888`。

## 三、 断点实验记录（修改请求参数）
**目的**：验证后端对参数为空时的校验逻辑，不修改前端代码，直接篡改请求。
- **目标接口**：`POST https://postman-echo.com/post`（回显型测试接口）
- **原始请求体**：`{"username": "admin", "password": "123456"}`
- **断点设置**：在 Charles 左侧列表右键该请求 -> `Breakpoints`。
- **拦截操作**：重新发送请求，Charles 拦截后，在 `Edit Request` 窗口底部的 **`JSON Text`** 标签页中，将 `password` 改为 `""`。点击 `Execute` 放行。
- **响应结果**：`json` 字段返回 `{"username": "admin", "password": ""}`，`content-length` 由 56 变为 41。
- **结论**：Charles 成功在请求到达服务端前篡改了参数。此方法常用于复现前端未校验的异常边界场景（如空密码、超长字符等）。

## 四、 抓包踩坑与排查经验（面试加分项）
1. **只看到 `CONNECT httpbin.org:443` 怎么办？**
   - 现象：左侧列表只显示 CONNECT 方法，看不到真实的 GET/POST 请求。
   - 原因：客户端与服务器建立了隧道，但 Charles 未成功解密。
   - 解决：检查证书是否被系统真正信任，以及 SSL Proxying 中是否添加了该域名。
2. **抓到的响应体是乱码怎么办？**
   - 现象：httpbin.org 等接口返回乱码。
   - 原因：服务端使用了 `br` (Brotli) 压缩，Charles 某些版本无法自动解压。
   - 解决：改用支持良好的接口（如 postman-echo.com），或排查 `Proxy` -> `Enable Transparent GZIP` 选项。
3. **断点弹出 `Edit Request` 窗口看不到请求体？**
   - 原因：Charles 默认显示 Overview（表头信息）。
   - 解决：点击窗口**最下方**的 `Text` 或 `JSON Text` 标签页即可查看并编辑 Body。

## 五、 Charles vs Apifox
- **Charles**：侧重于“抓”，看真实流量、前后端交互，用于定位问题；断点改参用于测试异常场景。
- **Apifox**：侧重于“发”，按测试用例主动构造请求，配合环境变量和断言，用于回归验证。