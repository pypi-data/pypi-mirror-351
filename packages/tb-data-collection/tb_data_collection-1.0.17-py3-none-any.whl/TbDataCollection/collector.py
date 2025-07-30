"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-01-17
Author: Martian Bugs
Description: 数据采集器
"""

from DrissionPage import Chromium, ChromiumOptions

from ._login import Login
from .branding.branding import Branding
from .myseller.myseller import Myseller
from .sycm.sycm import Sycm


class Collector:
    """采集器. 使用之前请先调用 `connect_browser` 方法连接浏览器."""

    def __init__(self):
        self._myseller = None
        self._sycm = None
        self._branding = None

    def connect_browser(self, port: int):
        """
        连接浏览器

        Args:
            port: 浏览器调试端口号
        """

        chrome_options = ChromiumOptions(read_file=False)
        chrome_options.set_local_port(port=port)

        self.browser = Chromium(addr_or_opts=chrome_options)

    def login(
        self,
        account: str,
        password: str,
        wait_captcha: float = None,
    ):
        """
        商家后台登录

        Args:
            account: 登录账号
            password: 登录密码
            wait_captcha: 等待验证码时间, 默认 10 分钟
        Returns:
            如果登录成功, 将返回操作的浏览器标签页对象
        """

        login_utils = Login(browser=self.browser)
        return login_utils.login(
            account=account, password=password, wait_captcha=wait_captcha
        )

    @property
    def myseller(self):
        if not self._myseller:
            self._myseller = Myseller(browser=self.browser)

        return self._myseller

    @property
    def sycm(self):
        if not self._sycm:
            self._sycm = Sycm(browser=self.browser)

        return self._sycm

    @property
    def branding(self):
        if not self._branding:
            self._branding = Branding(browser=self.browser)

        return self._branding
