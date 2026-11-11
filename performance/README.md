# 性能压测记录

## 1. 压测场景
- **被测接口**：`POST /api/login`（占比最高），兼顾 `GET /api/user/1` 与异常登录。
- **压测工具**：Locust 2.46.0 (Python 3.10)
- **压测环境**：本地 WSL2 Ubuntu，FastAPI (uvicorn 单进程)，Locust 同机运行。
- **执行命令**：
  ```bash
  locust -f performance/locustfile.py --headless -u 100 -r 10 -t 3m --csv=performance/reports/login_load --only-summary

## 核心指标
| 接口名称                        | 请求数   | RPS (QPS） | 平均响应时间 |  错误率 |
|-----------------------------|-------|-----------|--------|---|
| login_correct (正向登录)        | 6959  | 38.83     | 4ms    |   0.00%|
| login_wrong_password (异常登录） | 2318  | 12.93     |      4ms    |  0.00% |
| get_user_with_token (查用户)   | 2343  | 13.07     |   4ms       | 0.00%  |
| Aggregated (总计)             | 11720 | 65.39     |  4ms        |  0.00% |

## 结果分析
- 吞吐量表现：在 100 并发下，系统整体 QPS 稳定在 65 左右，任务权重（3:1:1）完全按预期分配。

- 稳定性：3 分钟内共发出 11720 次请求，错误率为 0%，说明当前 Mock 后端的纯内存逻辑十分稳定。

- 响应时间：业务接口的平均响应时间均在 4~6 ms，P95 控制在 10ms 以内，本地直连速度极快。

- 启动期分析：on_start_login 的最大响应时间达到 66ms，是因为前 10 秒内 100 个虚拟用户集中启动，瞬间并发对单进程后端造成了微小冲击；平稳期后响应时间恢复正常。