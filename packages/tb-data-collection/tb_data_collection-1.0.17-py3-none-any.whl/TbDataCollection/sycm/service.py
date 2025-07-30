"""
服务数据采集
"""

from random import uniform
from time import sleep
from typing import Callable

from DrissionPage import Chromium
from DrissionPage._units.downloader import DownloadMission

from .._utils import Utils
from ._utils import get__shop_name, pick__custom_date


class Urls:
    custom_report = (
        'https://sycm.taobao.com/qos/service/self_made_report#/self_made_report'
    )
    custom_service_performance = (
        'https://sycm.taobao.com/qos/service/frame/customer/performance/new#/user'
    )
    """客服绩效页面"""


class DataPacketUrls:
    custom_report__template_list = (
        'sycm.taobao.com/csp/api/customize/report/template/list'
    )
    """自制报表的模板列表"""
    custom_report__data_list__user = 'sycm.taobao.com/csp/api/user/customize/list.json'
    """自制报表数据列表接口-人员维度"""
    custom_report__data_list__shop = 'sycm.taobao.com/csp/api/shop/customize/list.json'
    """自制报表数据列表接口-店铺维度"""
    custom_report__download_task__user = (
        'sycm.taobao.com/csp/api/user/customize/async-excel'
    )
    """自制报表下载任务创建-人员维度"""
    custom_report__download_task__shop = (
        'sycm.taobao.com/csp/api/shop/customize/async-excel'
    )
    """自制报表下载任务创建-店铺维度"""
    custom_report__download_task__list = 'sycm.taobao.com/csp/api/file/task-list.json'
    """自制报表下载任务列表"""
    custom_report__download_task__file_url__get = 'sycm.taobao.com/csp/api/file/url'
    """自制报表下载任务文件下载地址获取"""
    custom_service_performance__as__solve = (
        'https://sycm.taobao.com/csp/api/aftsale/cst/list.json'
    )
    """客服绩效-售后分析-售后解决分析数据列表"""


class Service:
    def __init__(self, browser: Chromium):
        self._browser = browser
        self._timeout = 15

    def get__custom_report__detail(
        self, report_name: str, date: str, raw=False, timeout: float = None
    ):
        """
        获取自制报表数据

        Args:
            report_name: 报表名称
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        page = self._browser.new_tab()
        page.listen.start(
            targets=DataPacketUrls.custom_report__template_list,
            method='GET',
            res_type='XHR',
        )
        page.get(Urls.custom_report)
        template_packet = page.listen.wait(timeout=_timeout)
        if not template_packet:
            raise TimeoutError('进入页面后获取自制报表模板列表超时')

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
                filter(lambda x: x.get('reportTemplateName') == report_name, data), None
            )
            if not target_template:
                raise ValueError(f'未找到名为 {report_name} 的报表模板')

            return target_template

        target_template = parse_template_list()

        date_unsigned = date.replace('-', '')
        query_data = {
            'pageNo': 1,
            'pageSize': 100,
            'startDate': date_unsigned,
            'endDate': date_unsigned,
            'dateType': 'day',
            'dateRange': '1d',
            'reportTemplateId': target_template.get('id'),
        }

        api_path = (
            DataPacketUrls.custom_report__data_list__shop
            if target_template.get('reportTemplateType') == 0
            else DataPacketUrls.custom_report__data_list__user
        )
        api_url = f'https://{api_path}'
        page.change_mode('s', go=False)
        if not page.get(api_url, params=query_data, timeout=_timeout):
            raise RuntimeError('报表数据列表API请求失败')

        if (status_code := page.response.status_code) != 200:
            raise RuntimeError(f'报表数据列表API请求失败, 状态码: {status_code}')

        response = page.response.json()
        page.change_mode('d', go=False)
        if not isinstance(response, dict):
            raise ValueError('返回的数据包格式非预期的 dict 类型')

        if 'data' not in response:
            raise ValueError('返回的数据包中未找到 data 字段')
        data = response.get('data')
        if not isinstance(data, dict):
            raise ValueError('返回的数据包中的 data 字段非预期的 dict 类型')

        page.close()

        if raw is True:
            return data

        if 'dataSource' not in data:
            raise ValueError('返回的数据包中未找到 data.dataSource 字段')

        data_source: list[dict] = data.get('dataSource')
        if not isinstance(data_source, list):
            raise ValueError('返回的数据包中的 data.dataSource 字段非预期的 list 类型')

        if not data_source:
            return

        if 'columns' not in data:
            raise ValueError('返回的数据包中未找到 data.columns 字段')

        columns: list[dict] = data.get('columns')
        if not isinstance(columns, list):
            raise ValueError('返回的数据包中的 data.columns 字段非预期的 list 类型')

        columns: dict[str, dict] = {c['title']: c for c in columns}
        data_list: list[dict] = []
        for item in data_source:
            record = {t: item.get(c['dataIndex']) for t, c in columns.items()}
            data_list.append(record)

        need_format_columns = {t: c for t, c in columns.items() if c.get('unit')}

        def get_effective_indexs(t: str):
            return [i for i, item in enumerate(data_list) if item[t] is not None]

        for t, c in need_format_columns.items():
            unit: str = c['unit']
            if unit == 'percent':
                effect_indexs = get_effective_indexs(t)
                for i in effect_indexs:
                    data_list[i][t] = round(data_list[i][t] * 100, 2)
                continue

            if unit.startswith('.') and unit.endswith('f'):
                f_number = int(unit[1:-1])
                effect_indexs = get_effective_indexs(t)
                for i in effect_indexs:
                    data_list[i][t] = round(data_list[i][t], f_number)
                continue

            if unit == 'tc':
                # 效果: 4分23秒
                effect_indexs = get_effective_indexs(t)
                for i in effect_indexs:
                    value_formated = Utils.seconds_to_time(round(data_list[i][t]))
                    time_alias = ['时', '分', '秒']
                    _value = ''
                    for ii, v in enumerate(value_formated.split(':')):
                        if (_v := int(v)) == 0:
                            continue
                        _value += f'{_v}{time_alias[ii]}'
                    data_list[i][t] = _value
                continue

        return data_list

    def download__custom_report(
        self,
        report_name: str,
        date: str,
        save_path: str,
        save_name: str,
        extra_query_data: dict = None,
        timeout: float = None,
        download_wait_count: int = None,
    ):
        """
        下载自制报表

        Args:
            extra_query_data: 额外的下载任务创建API参数
            download_wait_count: 下载等待次数, 默认为 30 次
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout
        _download_wait_count = (
            download_wait_count if isinstance(download_wait_count, int) else 30
        )

        page = self._browser.new_tab()
        page.listen.start(
            targets=DataPacketUrls.custom_report__template_list,
            method='GET',
            res_type='XHR',
        )
        page.get(Urls.custom_report)
        template_packet = page.listen.wait(timeout=_timeout)
        if not template_packet:
            raise TimeoutError('进入页面后获取自制报表模板列表超时')

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
                filter(lambda x: x.get('reportTemplateName') == report_name, data), None
            )
            if not target_template:
                raise ValueError(f'未找到名为 {report_name} 的报表模板')

            return target_template

        target_template = parse_template_list()
        target_template_id = target_template.get('id')

        is_shop_dimension = target_template.get('reportTemplateType') == 0

        date_unsigned = date.replace('-', '')

        pub_req_headers = {'x-xsrf-token': page.cookies().as_dict().get('XSRF-TOKEN')}
        page.change_mode('s', go=False)

        def create__download_task():
            """请求API生成下载任务"""
            print('- 通过API创建下载任务')
            api_path = (
                DataPacketUrls.custom_report__download_task__shop
                if is_shop_dimension
                else DataPacketUrls.custom_report__download_task__user
            )
            api_url = f'https://{api_path}'
            query_data = {
                'startDate': date_unsigned,
                'endDate': date_unsigned,
                'dateType': 'day',
                'dateRange': '1d',
                'reportTemplateId': target_template_id,
                'bizCode': 'selfMadeReport',
            }
            if extra_query_data and isinstance(extra_query_data, dict):
                query_data.update(extra_query_data)

            if not page.get(
                api_url, params=query_data, headers=pub_req_headers, timeout=_timeout
            ):
                raise RuntimeError('创建下载任务API请求失败')

            response = page.response.json()
            if not isinstance(response, dict):
                raise ValueError('创建下载任务返回的数据包格式非预期的 dict 类型')

            return response.get('data')

        download_task_id = create__download_task()
        print(f'- 下载任务创建成功, ID: {download_task_id}')

        if not download_task_id:
            raise ValueError('创建下载任务失败, 下载任务ID为空')

        def get__download_task():
            """获取下载任务"""
            api_url = f'https://{DataPacketUrls.custom_report__download_task__list}'
            query_data = {'pageNo': 1, 'pageSize': 10, 'bizCode': 'selfMadeReport'}
            if not page.get(
                api_url, params=query_data, headers=pub_req_headers, timeout=_timeout
            ):
                raise RuntimeError('获取下载任务列表API请求失败')

            response = page.response.json()
            if not isinstance(response, dict):
                raise ValueError('下载任务列表返回的数据包格式非预期的 dict 类型')

            if 'data' not in response:
                raise ValueError('下载任务列表返回的数据包中未找到 data 字段')

            data = response.get('data')
            if not isinstance(data, dict):
                raise ValueError(
                    '下载任务列表返回的数据包中的 data 字段非预期的 dict 类型'
                )

            if 'result' not in data:
                raise ValueError('下载任务列表返回的数据包中未找到 data.result 字段')

            result: list[dict] = data.get('result')
            if not isinstance(result, list):
                raise ValueError(
                    '下载任务列表返回的数据包中的 data.result 字段非预期的 list 类型'
                )

            target_task: dict = next(
                filter(lambda x: x.get('id') == download_task_id, result), None
            )
            if not target_task:
                raise ValueError(f'未找到 ID 为 {download_task_id} 的下载任务')

            return target_task

        download_task = get__download_task()
        for _ in range(_download_wait_count):
            if download_task.get('process') == 100:
                break

            sleep(uniform(3.2, 3.5))
            download_task = get__download_task()
        else:
            raise TimeoutError('下载任务等待完成超时')

        def download__file():
            """下载文件"""
            api_url = (
                f'https://{DataPacketUrls.custom_report__download_task__file_url__get}'
            )
            query_data = {'id': download_task_id}
            if not page.get(
                api_url, params=query_data, headers=pub_req_headers, timeout=_timeout
            ):
                raise RuntimeError('获取下载文件地址API请求失败')

            response = page.response.json()
            if not isinstance(response, dict):
                raise ValueError('获取下载文件地址返回的数据包格式非预期的 dict 类型')

            if 'data' not in response:
                raise ValueError('获取下载文件地址返回的数据包中未找到 data 字段')

            file_url = response.get('data')
            if not isinstance(file_url, str):
                raise ValueError(
                    '获取下载文件地址返回的数据包中的 data 字段非预期的 str 类型'
                )

            page.change_mode('d', go=False)
            status, file_path = page.download(
                file_url=file_url,
                save_path=save_path,
                rename=save_name,
                file_exists='overwrite',
                show_msg=False,
            )
            if status != 'success':
                raise RuntimeError('文件下载失败')

            page.close()

            print(f'- 下载成功, 文件路径: {file_path}')
            return file_path

        return download__file()

    def download__custom_report__normal(
        self,
        report_name: str,
        date: str,
        save_path: str,
        save_name: str,
        timeout: float = None,
        download_wait_count: int = None,
        open_page=True,
        pre_callback: Callable = None,
        get_shop_name=False,
    ):
        """
        下载自制报表 (正常页面访问)

        Args:
            download_wait_count: 下载等待次数, 默认为 30 次
            open_page: 是否自动打开报表页面
            pre_callback: 点击下载前的回调函数, 接收一个参数: page (当前页面对象)
            get_shop_name: 是否获取店铺名称
        Returns:
            - 如果 get_shop_name 为 True, 则返回 (店铺名称, 文件路径)
            - 否则, 仅返回 文件路径
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout
        _download_wait_count = (
            download_wait_count if isinstance(download_wait_count, int) else 30
        )

        page = (
            self._browser.new_tab() if open_page is True else self._browser.latest_tab
        )
        if open_page is True:
            page.listen.start(
                targets=DataPacketUrls.custom_report__template_list,
                method='GET',
                res_type='XHR',
            )
            page.get(Urls.custom_report)
            template_packet = page.listen.wait(timeout=_timeout)
            if not template_packet:
                raise TimeoutError('进入页面后获取自制报表模板列表超时')

        template_btn = page.ele(
            f't:div@@class^ant-tabs-tab@@text()={report_name}', timeout=3
        )
        if not template_btn:
            raise ValueError(f'页面中未找到名为 [{report_name}] 的报表')

        if 'ant-tabs-tab-active' not in template_btn.attr('class'):
            page.listen.start(
                targets=[
                    DataPacketUrls.custom_report__data_list__shop,
                    DataPacketUrls.custom_report__data_list__user,
                ],
                method='GET',
                res_type='XHR',
            )
            template_btn.click(by_js=True)
            if not page.listen.wait(fit_count=False, timeout=_timeout):
                raise TimeoutError('点击报表按钮后获取报表数据超时')

        statistics_text = page.ele(
            't:div@@class=oui-date-picker-current-date', timeout=3
        )
        if not statistics_text:
            raise ValueError('页面中未找到[ 统计时间] 文本')

        statistics_date = statistics_text.text.strip()[5:]
        if statistics_date != date:
            page.listen.start(
                targets=[
                    DataPacketUrls.custom_report__data_list__shop,
                    DataPacketUrls.custom_report__data_list__user,
                ],
                method='GET',
                res_type='XHR',
            )
            pick__custom_date(date, page)
            if not page.listen.wait(fit_count=False, timeout=_timeout):
                raise TimeoutError('选择日期后获取报表数据超时')

        if pre_callback and callable(pre_callback):
            sleep(1)
            pre_callback(page)
            sleep(1)

        download_btn = page.ele('t:span@@text()=下载', timeout=3)
        if not download_btn:
            raise ValueError('页面中未找到[ 下载 ] 按钮')

        page.listen.start(
            targets=[
                DataPacketUrls.custom_report__download_task__shop,
                DataPacketUrls.custom_report__download_task__user,
            ],
            method='GET',
            res_type='XHR',
        )
        download_btn.click(by_js=True)
        task_packet = page.listen.wait(fit_count=False, timeout=_timeout)
        if not task_packet:
            raise TimeoutError('点击下载按钮后获取下载任务超时')

        task_resp: dict = task_packet.response.body
        if 'data' not in task_resp:
            raise ValueError('下载任务返回的数据包中未找到 data 字段')

        task_id = task_resp.get('data')
        if not task_id:
            raise ValueError('创建下载任务失败, 下载任务ID为空')

        pub_req_headers = {'x-xsrf-token': page.cookies().as_dict().get('XSRF-TOKEN')}
        page.change_mode('s', go=False)

        def get__task_obj():
            "获取下载任务对象"

            api_url = f'https://{DataPacketUrls.custom_report__download_task__list}'
            query_data = {'pageNo': 1, 'pageSize': 10, 'bizCode': 'selfMadeReport'}
            if not page.get(
                api_url, params=query_data, headers=pub_req_headers, timeout=_timeout
            ):
                raise RuntimeError('获取下载任务列表API请求失败')

            response = page.response.json()
            if not isinstance(response, dict):
                raise ValueError('下载任务列表返回的数据包格式非预期的 dict 类型')

            if 'data' not in response:
                raise ValueError('下载任务列表返回的数据包中未找到 data 字段')

            data = response.get('data')
            if not isinstance(data, dict):
                raise ValueError(
                    '下载任务列表返回的数据包中的 data 字段非预期的 dict 类型'
                )

            if 'result' not in data:
                raise ValueError('下载任务列表返回的数据包中未找到 data.result 字段')

            result: list[dict] = data.get('result')
            if not isinstance(result, list):
                raise ValueError(
                    '下载任务列表返回的数据包中的 data.result 字段非预期的 list 类型'
                )

            target_task: dict = next(
                filter(lambda x: x.get('id') == task_id, result), None
            )
            if not target_task:
                raise ValueError(f'未找到 ID 为 {task_id} 的下载任务')

            return target_task

        task_obj = get__task_obj()
        for _ in range(_download_wait_count):
            if task_obj.get('process') == 100:
                break

            sleep(uniform(3.2, 3.5))
            task_obj = get__task_obj()
        else:
            raise TimeoutError('下载任务等待完成超时')

        def download__file() -> str:
            """下载文件"""
            api_url = (
                f'https://{DataPacketUrls.custom_report__download_task__file_url__get}'
            )
            query_data = {'id': task_id}
            if not page.get(
                api_url, params=query_data, headers=pub_req_headers, timeout=_timeout
            ):
                raise RuntimeError('获取下载文件地址API请求失败')

            response = page.response.json()
            if not isinstance(response, dict):
                raise ValueError('获取下载文件地址返回的数据包格式非预期的 dict 类型')

            if 'data' not in response:
                raise ValueError('获取下载文件地址返回的数据包中未找到 data 字段')

            file_url = response.get('data')
            if not isinstance(file_url, str):
                raise ValueError(
                    '获取下载文件地址返回的数据包中的 data 字段非预期的 str 类型'
                )

            page.change_mode('d', go=False)
            status, file_path = page.download(
                file_url=file_url,
                save_path=save_path,
                rename=save_name,
                file_exists='overwrite',
                show_msg=False,
            )
            if status != 'success':
                raise RuntimeError('文件下载失败')

            return file_path

        result = file_path = download__file()

        if get_shop_name is True:
            shop_name = get__shop_name(page, throw_exception=False)
            result = shop_name, file_path

        if open_page is True:
            page.close()

        return result

    def download__customer_service_performance__as__solve(
        self,
        date: str,
        save_path: str,
        save_name: str,
        timeout: float = None,
        download_timeout: float = None,
    ):
        """
        下载 [客服绩效-售后分析-售后解决分析] 报表

        Args:
            timeout: 数据包超时时间, 默认为 15 秒
            download_timeout: 下载超时时间, 默认为 300 秒
        """

        page = self._browser.new_tab(Urls.custom_service_performance)
        as_btn = page.ele('t:span@@text()=售后分析', timeout=8)
        if not as_btn:
            raise RuntimeError('未找到 [售后分析] 按钮')
        sleep(1)
        as_btn.click(by_js=True)

        as_solve_btn = page.ele('t:span@@text()=售后解决分析', timeout=8)
        if not as_solve_btn:
            raise RuntimeError('未找到 [售后解决分析] 按钮')

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout

        def wait__packet(callback: Callable):
            page.listen.start(
                targets=DataPacketUrls.custom_service_performance__as__solve,
                method='GET',
                res_type='Fetch',
            )
            callback()
            packet = page.listen.wait(timeout=_timeout)
            if not packet:
                raise TimeoutError('获取 [售后解决分析] 数据超时')

        sleep(1)
        wait__packet(lambda: as_solve_btn.click(by_js=True))
        sleep(1.5)

        wait__packet(lambda: pick__custom_date(date, page))
        download_btn = page.ele('t:a@@text()=下载', timeout=3)
        if not download_btn:
            raise ValueError('页面中未找到[ 下载 ] 按钮')

        mission: DownloadMission = download_btn.click.to_download(
            save_path=save_path, rename=save_name, by_js=True, timeout=download_timeout
        )
        mission.wait(show=False, timeout=download_timeout)

        page.close()

        return mission.final_path
