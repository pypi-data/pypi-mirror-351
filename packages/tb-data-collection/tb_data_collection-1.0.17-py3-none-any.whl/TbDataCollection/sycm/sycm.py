"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-02-06
Author: Martian Bugs
Description: 生意参谋数据采集
"""

from DrissionPage import Chromium

from .goods import Goods
from .home import Home
from .self_analysis import SelfAnalysis
from .service import Service


class Sycm:
    def __init__(self, browser: Chromium):
        self._browser = browser

        self._home = None
        self._service = None
        self._self_analysis = None
        self._goods = None

    @property
    def home(self):
        """首页数据采集"""

        if not self._home:
            self._home = Home(self._browser)

        return self._home

    @property
    def service(self):
        """服务数据采集"""

        if not self._service:
            self._service = Service(self._browser)

        return self._service

    @property
    def self_analysis(self):
        """自助分析数据采集"""

        if not self._self_analysis:
            self._self_analysis = SelfAnalysis(self._browser)

        return self._self_analysis

    @property
    def goods(self):
        """商品模块数据采集"""

        if not self._goods:
            self._goods = Goods(self._browser)

        return self._goods
