"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-01-23
Author: Martian Bugs
Description: 千牛商家工作台数据采集模块
"""

from DrissionPage import Chromium

from .one import One


class Myseller:
    def __init__(self, browser: Chromium):
        self._browser = browser

        self._one = None

    @property
    def one(self):
        """万相台数据采集"""

        if not self._one:
            self._one = One(self._browser)

        return self._one
