"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-02-07
Author: Martian Bugs
Description: 品销宝数据采集
"""

from DrissionPage import Chromium

from .report import Report


class Branding:
    def __init__(self, browser: Chromium):
        self._browser = browser

        self._report = None

    @property
    def report(self):
        """报表模块数据采集"""

        if not self._report:
            self._report = Report(self._browser)

        return self._report
