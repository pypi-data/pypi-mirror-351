"""
报表模块数据采集
"""

from DrissionPage import Chromium

from .._utils import Utils
from ._dict import Dictionary


class Urls:
    star_shop = 'https://branding.taobao.com/?spm=a2e1zy.20166006.c0515d826.1.a09b58ddCchNC6#!/report/index?spm=a2e1zy.20166006.c0515d826.1.a09b58ddCchNC6&productid=101005202&effect=7&startdate={begin_date}&enddate={end_date}'


class DataPacketUrls:
    star_shop__overview = (
        'brandsearch.taobao.com/report/query/rptAdvertiserSubListNew.json'
    )


class Report:
    def __init__(self, browser: Chromium):
        self._browser = browser
        self._timeout = 15

    def get__star_shop__overview(
        self, begin_date: str, end_date: str, raw=False, timeout: float = None
    ):
        """
        获取明星店铺数据概览

        Returns:
            数据概览列表, {日期: {字段: 值}, ...}
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        page = self._browser.new_tab()
        page.listen.start(
            targets=DataPacketUrls.star_shop__overview, method='GET', res_type='XHR'
        )

        uri = Urls.star_shop.format(begin_date=begin_date, end_date=end_date)
        page.get(uri)
        packet = page.listen.wait(timeout=_timeout)
        if not packet:
            raise TimeoutError('进入首页数据包获取超时')

        response = packet.response.body
        if not isinstance(response, dict):
            raise ValueError('返回的数据包非预期的 dict 类型')

        if 'data' not in response:
            raise ValueError('返回的数据包中未找到 data 字段')

        data = response['data']
        if not isinstance(data, dict):
            raise ValueError('返回的数据包中 data 字段非预期的 dict 类型')

        if 'rptQueryResp' not in data:
            raise ValueError('返回的数据包中未找到 data.rptQueryResp 字段')

        rpt_query_resp = data['rptQueryResp']
        if not isinstance(rpt_query_resp, dict):
            raise ValueError('返回的数据包中 data.rptQueryResp 字段非预期的 dict 类型')

        if 'rptDataDaily' not in rpt_query_resp:
            raise ValueError('返回的数据包中未找到 data.rptQueryResp.rptDataDaily 字段')

        rpt_data_daily: list[dict] = rpt_query_resp['rptDataDaily']
        if not isinstance(rpt_data_daily, list):
            raise ValueError(
                '返回的数据包中 data.rptQueryResp.rptDataDaily 字段非预期的 list 类型'
            )

        page.close()

        if not rpt_data_daily:
            return

        data_list = sorted(rpt_data_daily, key=lambda x: x['thedate'])
        dates = [x['thedate'] for x in data_list]
        data_list = data_list[dates.index(begin_date) : dates.index(end_date) + 1]

        if raw is True:
            return data_list

        records: dict[str, dict] = {}
        for item in data_list:
            date = item['thedate']
            record = Utils.dict_mapping(item, Dictionary.report.star_shop__overview)
            record = Utils.dict_format__float(
                record,
                fields=[
                    '消耗',
                    '点击单价',
                    '跳转点击单价',
                    '成交金额',
                    '自然流量增量成交',
                ],
            )
            record = Utils.dict_format__ratio(
                record,
                fields=[
                    '点击率',
                    '转化率',
                    '访客触达率',
                    '搜索进店率',
                    '进店行动率',
                    '行动成交率',
                ],
            )
            record = Utils.dict_format__round(record)
            records[date] = record

        return records
