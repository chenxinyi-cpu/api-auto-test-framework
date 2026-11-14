import json
from playwright.sync_api import Page
from web_ui.pages.base_page import BasePage

class LoginPage(BasePage):

    URL = "http://127.0.0.1:8000/docs"

    def __init__(self,page:Page):
        super().__init__(page)


    #------------------定位器----------------------
    @property
    def login_api_button(self):
        return self.page.get_by_role("button",name="post /api/login",exact=True)

    @property
    def try_it_out_button(self):
        return self.page.get_by_role("button",name="Try it out")

    @property
    def request_body_input(self):
        return self.page.locator("textarea").first

    @property
    def execute_button(self):
        return self.page.get_by_role("button",name="Execute")


    #------------------动作方法--------------------
    def click_login_api(self):
        self.login_api_button.click()
        return self

    def click_try_it_out(self):
        self.try_it_out_button.click()
        return self

    def fill_login_body(self,username:str,password:str):
        body_data = {"username":username,"password":password}
        json_str = json.dumps(body_data,ensure_ascii=False,indent=2)
        self.request_body_input.fill(json_str)
        return self

    def click_execute(self):
        self.execute_button.click()
        return self

