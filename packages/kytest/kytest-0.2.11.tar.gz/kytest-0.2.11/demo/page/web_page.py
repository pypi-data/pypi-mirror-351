"""
@Author: kang.yang
@Date: 2024/9/14 09:48
"""
import kytest
from kytest.core.web import Elem


class LoginPage(kytest.Page):
    url = "https://www-test.qizhidao.com/login?redirect=https%3A%2F%2Fwww-test.qizhidao.com%2F&businessSource" \
          "=PC%E7%BB%BC%E5%90%88-%E9%A1%B6%E9%83%A8%E6%A8%A1%E5%9D%97-%E7%AB%8B%E5%8D%B3%E7%99%BB%E5%BD%95&" \
          "registerPage=https%3A%2F%2Fwww-test.qizhidao.com%2F&fromPage=home"

    login_or_reg = Elem(text="登录/注册", exact=True)
    pwd_login = Elem(text='密码登录')
    phone_input = Elem(placeholder='请输入手机号码')
    pwd_input = Elem(placeholder='请输入密码')
    accept = \
        Elem(locator='form div') \
            .filter(has_text="我已阅读并同意《企知道平台服务协议》、 《企知道隐私权政策》、 《企知道商城/商贸空间使用须知》") \
            .locator("span") \
            .nth(3)
    login_now = Elem(role='button', name='立即登录')
    first_company = Elem().get_by_text('北京大胖涮锅城有限公司')
