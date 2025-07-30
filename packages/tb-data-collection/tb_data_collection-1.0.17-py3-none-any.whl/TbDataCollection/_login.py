"""
处理千牛工作台登录逻辑
"""

from contextlib import suppress
from time import sleep
from urllib.parse import unquote

from DrissionPage import Chromium
from DrissionPage._pages.mix_tab import MixTab
from DrissionPage.errors import ContextLostError, ElementLostError

from ._utils import Utils


class Urls:
    home = 'https://myseller.taobao.com/'
    login = 'https://loginmyseller.taobao.com/'


class Login:
    def __init__(self, browser: Chromium):
        self._browser = browser

    def _get__logined_account_name(self, page: MixTab):
        """
        获取当前已登录的用户的用户名

        Returns:
            当前登录的用户名
        """

        sn = page.cookies().as_dict().get('sn')
        account_name = unquote(sn) if sn else None
        return account_name

    def _check__login_captcha(self, page: MixTab, timeout: float = None):
        """判断登录时是否出现了验证码"""

        captcha_input = page.ele('#J_Checkcode', timeout=8)
        if not captcha_input:
            return True

        _timeout = timeout if isinstance(timeout, (int, float)) else 10 * 60
        with suppress(ContextLostError, ElementLostError):
            if not captcha_input.wait.disabled_or_deleted(timeout=_timeout):
                return False

        return True

    def login(self, account: str, password: str, wait_captcha: float = None):
        """
        登录千牛后台

        Args:
            account: 登陆账号
            password: 登陆密码
            wait_captcha: 等待验证码出现的超时时间，默认10分钟
        Returns:
            登录时操作的浏览器标签页对象
        """

        page = self._browser.latest_tab

        if not Utils.same_url(page.url, Urls.login):
            page.get(Urls.home)

        if not page.wait.url_change(Urls.login, timeout=3):
            logined_account = self._get__logined_account_name(page)
            if logined_account != account:
                raise RuntimeError(
                    f'当前已登录的用户 {logined_account} 与目标用户 {account} 不一致'
                )

            return page

        sleep(0.5)
        account_input = page.ele('#fm-login-id', timeout=3)
        if not account_input:
            raise RuntimeError('未能找到 [登录名输入框] 元素')
        sleep(1)
        account_input.input(account, clear=True)

        passwd_input = page.ele('#fm-login-password', timeout=3)
        if not passwd_input:
            raise RuntimeError('未能找到 [密码输入框] 元素')
        sleep(1)
        passwd_input.input(password, clear=True)

        login_btn = page.ele('t:button@@text()=登录', timeout=3)
        if not login_btn:
            raise RuntimeError('未能找到 [登录按钮] 元素')
        login_btn.click()

        if not self._check__login_captcha(page, wait_captcha):
            raise RuntimeError('登录超时')

        if not page.wait.url_change('QnworkbenchHome', timeout=8):
            raise RuntimeError('登录失败')

        return page
