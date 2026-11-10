# 基于 Pytest + Requests 的多环境接口自动化回归框架

## 项目背景

后端用户管理接口迭代频繁，手工回归重复工作量大，容易漏测边界和异常场景。
本框架基于 Pytest + Requests 搭建数据驱动自动化回归方案，用于接口冒烟回归和全量回归，替代手工重复劳动，提升回归效率。

## 技术栈

- **语言**：Python 3.10
- **测试框架**：pytest、pytest-rerunfailures
- **请求库**：requests
- **数据驱动**：PyYAML
- **测试报告**：allure-pytest、Allure 命令行
- **被测后端**：FastAPI（本地 Mock）

## 核心特性

1. **多环境配置**：`config/env.yaml` 修改 `current_env` 即可切换 dev/test，零代码修改。
2. **数据驱动**：用例存放在 `cases/*.yaml`，用例与代码分离；新增接口只加 yaml 和 test 脚本，不改底层封装。
3. **统一请求封装**：`common/request_util.py` 统一处理 base_url 拼接、token 注入、超时、异常捕获、请求/响应日志。
4. **session 级登录复用**：`conftest.py` 中 `login_token` fixture 使用 `scope="session"`，一次登录，全局共享 token。
5. **冒烟/全量策略**：利用 pytest marker 和 yaml 中的 `smoke: true`，支持 `pytest -m smoke` 秒级快速验证。
6. **失败自动重试**：`pytest-rerunfailures` 失败自动重跑 2 次，过滤偶发网络抖动（注意：重试不能掩盖真实 Bug）。
7. **Allure 可视化报告**：用例按 feature/story 分组，展示用例标题、请求日志、重试记录。

## 项目结构

```text
api-auto-test-framework/
├── cases/                  # yaml 数据驱动用例
│   ├── login_case.yaml
│   └── get_user_case.yaml
├── common/                 # 公共工具层
│   ├── log_util.py         # 日志封装
│   ├── request_util.py     # 统一请求封装
│   └── yaml_util.py        # yaml 读取工具
├── config/
│   └── env.yaml            # 多环境配置
├── docs/                   # 抓包、bug单、Allure报告截图
├── mock_server/            # FastAPI 被测后端
├── sql/                    # SQL 练习脚本
├── test_cases/             # pytest 测试脚本层
│   ├── test_login.py
│   └── test_get_user.py
├── conftest.py             # 全局 fixture（登录获取 token）
├── pytest.ini              # pytest 配置（marker 注册、重试、testpaths）
├── requirements.txt        # 依赖清单
├── TODO.md                 # 待办事项
└── README.md
```
## 被测系统
本地 FastAPI Mock 后端，包含 4 个接口：登录、查询用户、修改用户、删除用户。

启动命令：python mock_server/main.py

接口文档：http://127.0.0.1:8000/docs

## 环境安装
```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 安装 Allure 命令行工具（用于生成报告）
# Windows: 下载 zip 解压并配置环境变量
# Mac/Linux: brew install allure 或 apt install allure
```

## 执行命令
```bash
# 1. 运行全量回归并生成 Allure 原始数据
pytest -v --alluredir=reports/allure-results

# 2. 启动服务查看 Allure 可视化报告
allure serve reports/allure-results

# 3. 仅运行冒烟用例（快速验证）
pytest -m smoke -v
```

## 报告截图
docs/allure_report.png


## CI 持续集成

项目配置了 GitHub Actions，每次 push 到 `main` 或提交 Pull Request 自动触发：
1. 拉取代码，安装 Python 3.10 和项目依赖
2. 后台启动 FastAPI Mock 后端，健康检查通过后执行
3. 运行 `pytest -m smoke` 冒烟用例
4. 上传 Allure 原始结果作为 artifact（即使测试失败也可下载）

## 项目局限
本框架只做接口功能校验，不替代探索性测试；自动化无法覆盖 UI 体验类问题。

频繁改动的业务接口维护成本高，不适合自动化。

重试机制能过滤网络抖动，但可能掩盖真实的间歇性 Bug，需配合日志排查。




