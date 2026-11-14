import pytest
from playwright.sync_api import expect
from web_ui.pages.login_page import LoginPage


@pytest.mark.ui
def test_login_success(page):
    login_page = LoginPage(page)
    login_page.open().click_login_api().click_try_it_out().fill_login_body("admin","123456").click_execute()
    expect(page.get_by_text("mock-token-abc123")).to_be_visible(timeout=5000)



@pytest.mark.ui
def test_login_wrong_password(page):
    login_page = LoginPage(page)

    login_page.open() \
        .click_login_api() \
        .click_try_it_out() \
        .fill_login_body("admin", "wrong_password") \
        .click_execute()

    expect(page.get_by_text("账号或密码错误")).to_be_visible(timeout=5000)