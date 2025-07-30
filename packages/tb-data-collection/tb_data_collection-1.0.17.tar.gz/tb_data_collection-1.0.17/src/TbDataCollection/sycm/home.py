"""
首页数据采集
"""

from time import time

from DrissionPage import Chromium
from tenacity import retry, stop_after_attempt, wait_fixed

from .._utils import Utils
from ._dict import Dictionary


class Urls:
    home = 'https://sycm.taobao.com/portal/home.htm'


class DataPacketUrls:
    home__overall__live_overview = 'sycm.taobao.com/portal/live/new/index/overview.json'
    """整体数据概览-实时数据"""
    home__overall__live_overview__v3 = (
        'sycm.taobao.com/portal/live/new/index/overview/v3.json'
    )
    home__overall__overview = 'sycm.taobao.com/portal/coreIndex/new/overview/v2.json'


class Home:
    def __init__(self, browser: Chromium):
        self._browser = browser
        self._timeout = 15

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), reraise=True)
    def get__overall__overview(self, date: str, timeout: float = None, raw=False):
        """获取首页整体看板概览数据"""

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        page = self._browser.new_tab()
        page.listen.start(
            targets=[
                DataPacketUrls.home__overall__live_overview,
                DataPacketUrls.home__overall__live_overview__v3,
            ],
            method='GET',
            res_type='Fetch',
        )
        page.get(Urls.home)
        packet = page.listen.wait(timeout=_timeout, count=1, fit_count=True)
        if not packet:
            raise TimeoutError('首次进入页面获取概览数据超时')

        query_token = packet.request.params.get('token')

        query_data = {
            'needCycleCrc': True,
            'dateType': 'day',
            'dateRange': f'{date}|{date}',
            '_': int(time() * 1000),
            'token': query_token,
        }

        page.change_mode('s', go=False)
        api_url = f'https://{DataPacketUrls.home__overall__overview}'
        if not page.get(api_url, params=query_data):
            raise RuntimeError('API请求失败')

        if (status_code := page.response.status_code) != 200:
            raise RuntimeError(f'API请求失败, 状态码: {status_code}')

        response = page.response.json()
        page.change_mode('d', go=False)
        if not isinstance(response, dict):
            raise RuntimeError('返回数据格式错误, 非预期的 dict 类型')

        if 'content' not in response:
            raise RuntimeError('返回的数据包中未找到 content 字段')

        content = response.get('content')
        if not isinstance(content, dict):
            raise RuntimeError('数据包中的 content 字段数据格式非预期的 dict 类型')

        if 'data' not in content:
            raise RuntimeError('数据包中的 content 字段中未找到 data 字段')

        data = content.get('data')
        if not isinstance(data, dict):
            raise RuntimeError('数据包中的 content.data 字段数据格式非预期的 dict 类型')

        if 'self' not in data:
            raise RuntimeError('数据包中的 content.data 字段中未找到 self 字段')

        _self = data.get('self')
        if not isinstance(_self, dict):
            raise RuntimeError(
                '数据包中的 content.data.self 字段数据格式非预期的 dict 类型'
            )

        page.close()

        if raw is True:
            return _self

        record: dict[str, dict] = Utils.dict_mapping(
            _self, Dictionary.home.overall__overview
        )
        record = {k: v.get('value') for k, v in record.items() if isinstance(v, dict)}

        record = Utils.dict_format__ratio(
            record, fields=['老客复购率', '咨询率', '24小时揽收及时率', '成功退款率']
        )
        record = Utils.dict_format__round(record)

        return record
