import os

import pytest

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport":{"width":1400,"height":900},
    }

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item,call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            # 1. 确保截图目录存在
            report_dir = "web_ui/reports"
            os.makedirs(report_dir, exist_ok=True)

            # 2. 拼接路径
            screenshot_path = os.path.join(report_dir, f"fail_{item.name}.png")

            # 3. 传入 path 参数截图
            page.screenshot(path=screenshot_path)
            print(f"\n[失败自动截图已保存]: {screenshot_path}")
