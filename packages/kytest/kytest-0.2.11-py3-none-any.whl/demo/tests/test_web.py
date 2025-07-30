"""
@Author: kang.yang
@Date: 2023/11/16 17:50
"""
import kytest
from kytest.core.web import TC
from page.web_page import LoginPage


@kytest.story('登录模块')
class TestWebDemo(TC):
    def start(self):
        self.LP = LoginPage(self.dr)

    @kytest.title("登录")
    def test_login(self):
        self.LP.goto()
        self.LP.pwd_login.click()
        self.sleep(5)





