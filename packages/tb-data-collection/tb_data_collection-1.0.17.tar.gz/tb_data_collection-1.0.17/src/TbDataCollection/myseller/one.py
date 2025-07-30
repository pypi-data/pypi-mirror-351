"""
推广中心-万相台 数据采集
"""

from random import uniform
from time import sleep

from DrissionPage import Chromium
from DrissionPage._pages.mix_tab import MixTab

from .._utils import Utils
from ._dict import Dictionary
from ._utils import Pagination


class Urls:
    marketing_scenario = 'https://one.alimama.com/index.html?spm=a21dvs.28490323.cff91601f.d02a58bac.2b022d699GNcKU#!/report/account?spm=a21dvs.28490323.cff91601f.d02a58bac.2b022d699GNcKU&rptType=account&startTime={begin_date}&endTime={end_date}&vsType=off'
    """营销场景报表页面"""

    short_video = 'https://one.alimama.com/index.html?spm=a21dvs.28490323.cff91601f.d02a58bac.2b022d69ldMIMO#!/report/short_video_migrate?spm=a21dvs.28490323.cff91601f.d02a58bac.2b022d69ldMIMO&rptType=short_video_migrate&bizCode=onebpShortVideo&startTime={begin_date}&endTime={end_date}'
    """短视频报表页面"""

    item_promotion = 'https://one.alimama.com/index.html?spm=a21dvs.28490323.cff91601f.d02a58bac.2b022d69OoZjJ1#!/report/item_promotion?spm=a21dvs.28490323.cff91601f.d02a58bac.2b022d69OoZjJ1&rptType=item_promotion&startTime={begin_date}&endTime={end_date}'
    """主体报表页面"""

    item_promotion__by_goods = 'https://one.alimama.com/index.html?spm=a21dvs.28490323.cff91601f.d02a58bac.2b02645eefxKOV#!/report/item_promotion?spm=a21dvs.28490323.cff91601f.d02a58bac.2b02645eefxKOV&rptType=item_promotion&startTime={begin_date}&endTime={end_date}&offset=0&searchKey=itemIdOrName&searchValue={goods_id}'
    """主体报表页面-按商品ID查询"""


class DataPacketUrls:
    general_query = 'one.alimama.com/report/query.json'


class One:
    def __init__(self, browser: Chromium):
        self._browser = browser
        self._timeout = 15

    def _wait__general_query_packet(
        self,
        page: MixTab,
        begin_date: str,
        end_date: str,
        query_domains: list[str],
        timeout: float = None,
    ):
        """
        等待通用数据查询接口数据包监听返回
        - 需要手动开启数据包监听
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        packet = None
        for item in page.listen.steps(count=None, gap=1, timeout=_timeout):
            reqdata: dict = item.request.postData
            if reqdata.get('queryDomains') != query_domains:
                continue

            if (
                reqdata.get('startTime') != begin_date
                or reqdata.get('endTime') != end_date
            ):
                continue

            packet = item
            break

        return packet

    def get__marketing_scenario__overview(
        self,
        begin_date: str,
        end_date: str,
        is_international=False,
        timeout: float = None,
        raw=False,
    ):
        """
        获取营销场景报表概览

        Args:
            is_international: 是否为国际店
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        page = self._browser.new_tab()

        uri = Urls.marketing_scenario.format(begin_date=begin_date, end_date=end_date)
        data_packet_url = DataPacketUrls.general_query
        if is_international is True:
            uri = uri.replace('.com', '.hk')
            data_packet_url = data_packet_url.replace('.com', '.hk')

        page.listen.start(targets=data_packet_url, method='POST', res_type='XHR')
        page.get(uri)

        packet = self._wait__general_query_packet(
            page, begin_date, end_date, ['account'], timeout=_timeout
        )
        if not packet:
            raise TimeoutError('数据包监听超时')

        resp: dict = packet.response.body
        if 'data' not in resp:
            raise ValueError('数据包中未找到 data 字段')

        data: dict = resp.get('data')
        if not isinstance(data, dict):
            raise ValueError('数据包中的 data 字段非预期的 dict 类型')

        page.close()

        if raw is True:
            return data

        if 'list' not in data:
            raise ValueError('数据包中未找到 data.list 字段')

        list_data: list = data.get('list')
        if not isinstance(list_data, list):
            raise ValueError('数据包中的 data.list 字段非预期的 list 类型')

        if not list_data:
            raise ValueError('数据包中的 data.list 字段为空列表')

        record: dict = list_data[0]
        record = Utils.dict_mapping(record, Dictionary.one.marketing_scenario__overview)
        record = Utils.dict_format__ratio(record, ['点击率', '点击转化率'])
        record = Utils.dict_format__round(record)

        return record

    def get__short_video__overview(
        self,
        begin_date: str,
        end_date: str,
        is_international=False,
        timeout: float = None,
        raw=False,
    ):
        """获取短视频报表概览"""

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        page = self._browser.new_tab()
        uri = Urls.short_video.format(begin_date=begin_date, end_date=end_date)
        data_packet_url = DataPacketUrls.general_query
        if is_international is True:
            uri = uri.replace('.com', '.hk')
            data_packet_url = data_packet_url.replace('.com', '.hk')

        page.listen.start(targets=data_packet_url, method='POST', res_type='XHR')
        page.get(uri)

        packet = self._wait__general_query_packet(
            page, begin_date, end_date, ['account'], timeout=_timeout
        )
        if not packet:
            raise TimeoutError('数据包监听超时')

        resp: dict = packet.response.body
        if 'data' not in resp:
            raise ValueError('数据包中未找到 data 字段')

        data: dict = resp.get('data')
        if not isinstance(data, dict):
            raise ValueError('数据包中的 data 字段非预期的 dict 类型')

        page.close()

        if raw is True:
            return data

        if 'list' not in data:
            raise ValueError('数据包中未找到 data.list 字段')

        list_data: list = data.get('list')
        if not isinstance(list_data, list):
            raise ValueError('数据包中的 data.list 字段非预期的 list 类型')

        if not list_data:
            raise ValueError('数据包中的 data.list 字段为空列表')

        record: dict = list_data[0]
        record = Utils.dict_mapping(record, Dictionary.one.short_video__overview)

        return record

    def get__item_promotion__goods__detail(
        self,
        goods_ids: list[str],
        date: str,
        is_international=False,
        raw=False,
        timeout: float = None,
    ):
        """获取指定商品的主体报表数据"""

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        page = self._browser.new_tab()
        uri = Urls.item_promotion.format(begin_date=date, end_date=date)
        data_packet_url = DataPacketUrls.general_query
        if is_international is True:
            uri = uri.replace('.com', '.hk')
            data_packet_url = data_packet_url.replace('.com', '.hk')

        page.listen.start(targets=data_packet_url, method='POST', res_type='XHR')
        page.get(uri)

        if not self._wait__general_query_packet(
            page, date, date, ['promotion'], timeout=_timeout
        ):
            raise TimeoutError('首次进入页面数据包获取超时')

        # ========== 修改页面大小 ==========
        page.listen.start(targets=data_packet_url, method='POST', res_type='XHR')
        Pagination.set__max_page_size(page)
        packet = self._wait__general_query_packet(
            page, date, date, ['promotion'], timeout=_timeout
        )
        # ========== 修改页面大小 ==========

        resp: dict = packet.response.body
        if 'data' not in resp:
            raise ValueError('数据包中未找到 data 字段')

        data: dict = resp.get('data')
        if not isinstance(data, dict):
            raise ValueError('数据包中的 data 字段非预期的 dict 类型')

        if 'list' not in data:
            raise ValueError('数据包中未找到 data.list 字段')
        raw_data_list: list[dict] = data['list']

        if raw is True:
            page.close()
            return raw_data_list

        _goods_ids = [str(g) for g in goods_ids]

        data_list: dict[str, dict] = {}
        while len(_goods_ids) > 0:
            for item in raw_data_list:
                goods_id = str(item.get('promotionId'))
                if goods_id not in _goods_ids:
                    continue

                data_list[goods_id] = item
                _goods_ids.remove(goods_id)

            if not _goods_ids:
                break

            sleep(uniform(2.2, 3.2))

            page.listen.start(targets=data_packet_url, method='POST', res_type='XHR')
            Pagination.next_page(page)
            packet = self._wait__general_query_packet(
                page, date, date, ['promotion'], timeout=_timeout
            )
            if not packet:
                break

            resp: dict = packet.response.body
            try:
                data: dict = resp.get('data')
                raw_data_list: list[dict] = data.get('list')
            except Exception as e:
                print(f'下一页数据包解析出错: {e}')
                break

        records: dict[str, dict] = {}
        for goods_id, data in data_list.items():
            record = Utils.dict_mapping(
                data, Dictionary.one.item_promotion__goods__detail
            )
            record = Utils.dict_format__ratio(record, fields=['点击率', '点击转化率'])
            record = Utils.dict_format__round(record)
            records[goods_id] = record

        page.close()

        return records

    def get__item_promotion__goods__detail__by_goods(
        self,
        goods_id: str,
        begin_date: str,
        end_date: str,
        is_international=False,
        raw=False,
        timeout: float = None,
    ):
        """获取指定商品id的主体报表数据"""

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        page = self._browser.new_tab()
        uri = Urls.item_promotion__by_goods.format(
            begin_date=begin_date, end_date=end_date, goods_id=goods_id
        )
        data_packet_url = DataPacketUrls.general_query
        if is_international is True:
            uri = uri.replace('.com', '.hk')
            data_packet_url = data_packet_url.replace('.com', '.hk')

        page.listen.start(targets=data_packet_url, method='POST', res_type='XHR')
        page.get(uri)

        packet = self._wait__general_query_packet(
            page, begin_date, end_date, ['promotion'], timeout=_timeout
        )
        if not packet:
            raise TimeoutError('进入页面后数据包获取超时')

        resp = packet.response.body
        if not isinstance(resp, dict):
            raise ValueError('返回的数据包非预期的 dict 类型')

        if 'data' not in resp:
            raise ValueError('数据包中未找到 data 字段')

        data = resp['data']
        if not isinstance(data, dict):
            raise ValueError('数据包中的 data 字段非预期的 dict 类型')

        if 'list' not in data:
            raise ValueError('数据包中未找到 data.list 字段')

        data_list = data['list']
        if not isinstance(data_list, list):
            raise ValueError('数据包中的 data.list 字段非预期的 list 类型')

        item_data = next(
            filter(lambda x: str(x.get('promotionId')) == goods_id, data_list), None
        )

        page.close()
        if not item_data or raw is True:
            return item_data

        record = Utils.dict_mapping(
            item_data, Dictionary.one.item_promotion__goods__detail
        )
        record = Utils.dict_format__ratio(record, fields=['点击率', '点击转化率'])
        record = Utils.dict_format__round(record)

        return record
