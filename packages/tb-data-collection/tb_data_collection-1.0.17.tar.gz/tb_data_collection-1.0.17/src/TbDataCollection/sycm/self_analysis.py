"""
自助分析数据采集
"""

from time import time

from DrissionPage import Chromium

from .._utils import Utils


class Urls:
    fetch_report__my = 'https://sycm.taobao.com/adm/v3/my_space?tab=fetch'
    """个人空间-取数报表页面"""


class DataPacketUrls:
    fetch_report__template_list__my = 'sycm.taobao.com/adm/v3/report/my.json'
    """个人空间-取数报表列表"""
    fetch_report__detail__preview = 'sycm.taobao.com/adm/v2/execute/previewById.json'
    """取数报表数据预览"""


class SelfAnalysis:
    def __init__(self, browser: Chromium):
        self._browser = browser
        self._timeout = 15

    def get__fetch_report__detail__my(
        self,
        report_name: str,
        begin_date: str,
        end_date: str,
        raw=False,
        timeout: float = None,
    ):
        """
        获取个人空间-指定取数报表数据
        - 只能获取最近 10 天的数据

        Args:
            report_name: 报表名称
        Returns:
            报表数据列表 {日期: {字段: 值}, ...}
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        page = self._browser.new_tab()
        page.listen.start(
            targets=DataPacketUrls.fetch_report__template_list__my,
            method='GET',
            res_type='Fetch',
        )
        page.get(Urls.fetch_report__my)
        template_packet = page.listen.wait(timeout=_timeout)
        if not template_packet:
            raise TimeoutError('进入页面后获取取数报表模板列表超时')

        query_token = template_packet.request.params.get('token')

        def parse_template_list():
            """解析模板列表获取指定模板的数据对象"""
            template_response: dict = template_packet.response.body
            if 'data' not in template_response:
                raise ValueError('解析报表模板列表出错, 数据包中未找到 data 字段')
            data = template_response.get('data')
            if not isinstance(data, list):
                raise ValueError(
                    '解析报表模板列表出错, 数据包中的 data 字段非预期的 list 类型'
                )
            target_template: dict = next(
                filter(lambda x: x.get('name') == report_name, data), None
            )
            if not target_template:
                raise ValueError(f'未找到名为 {report_name} 的报表模板')

            return target_template

        target_template = parse_template_list()

        query_data = {
            'id': target_template.get('id'),
            'reportType': '1',
            '_': int(time() * 1000),
            'token': query_token,
        }

        page.change_mode('s', go=False)
        api_url = f'https://{DataPacketUrls.fetch_report__detail__preview}'
        if not page.get(api_url, params=query_data):
            raise RuntimeError('API请求失败')

        if (status_code := page.response.status_code) != 200:
            raise RuntimeError(f'API请求失败, 状态码: {status_code}')

        response = page.response.json()
        page.change_mode('d', go=False)
        page.change_mode('d', go=False)
        if not isinstance(response, dict):
            raise RuntimeError('返回数据格式错误, 非预期的 dict 类型')

        if 'data' not in response:
            raise RuntimeError('返回的数据包中未找到 data 字段')

        data = response.get('data')
        if not isinstance(data, dict):
            raise RuntimeError('数据包中的 data 字段数据格式非预期的 dict 类型')

        page.close()

        if raw is True:
            return data

        if 'data' not in data or 'title' not in data:
            raise ValueError('数据包中未找到 data.data 或 data.title 字段')

        title = data.get('title')
        data_source = data.get('data')

        data_list: list[dict] = []
        for item in data_source:
            data_list.append(dict(zip(title, item)))
        data_list = sorted(data_list, key=lambda x: x.get('统计日期'))

        dates = [item.get('统计日期') for item in data_list]
        data_list = data_list[dates.index(begin_date) : dates.index(end_date) + 1]

        records: dict[str, dict] = {}
        for item in data_list:
            date = item['统计日期']
            record = Utils.dict_format__strip(item, suffix=['%'])
            record = Utils.dict_format__number(record)
            records[date] = record

        return records
