import os
from playwright.sync_api import Page

class BasePage:

    URL = None
    REPORTS_DIR = "web_ui/reports"

    def __init__(self,page:Page):
        self.page = page

    def open(self):
        if self.URL:
            self.page.goto(self.URL)
        return self

    def title(self)->str:
        return self.page.title()

    def screenshot(self,name:str,**kwargs):
        os.makedirs(self.REPORTS_DIR,exist_ok=True)
        path = os.path.join(self.REPORTS_DIR,f"{name}.png")
        self.page.screenshot(path=path,**kwargs)
        print(f"[截图已保存]:{path}")
        return path