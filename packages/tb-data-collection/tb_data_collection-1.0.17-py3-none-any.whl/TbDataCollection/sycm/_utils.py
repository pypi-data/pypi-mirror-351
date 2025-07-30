import json
import re
from time import sleep

from DrissionPage._pages.mix_tab import MixTab


def parse__localstorage_data(content: str):
    """解析格式化 localStorage 数据"""

    _data = re.sub(r'^\d+\|', '', content.strip('"').replace('\\', ''))
    data_json: dict = json.loads(_data)
    value: dict = data_json.get('value')

    return value.get('_d')


def pick__custom_date(date: str, page: MixTab):
    """选择自定义日期"""

    selector = page.ele('t:button@@class^ant-btn@@text()=日', timeout=3)
    if not selector:
        raise RuntimeError('未找到日期选择器')

    selector.hover()
    sleep(0.5)

    year, month, _ = date.split('-')
    month = month.lstrip('0')

    year_btn = page.ele('c:span.oui-dt-calendar-control.year', timeout=3)
    if not year_btn:
        raise RuntimeError('未找到年份切换按钮')

    curr_year = year_btn.text.strip().rstrip('年')
    if curr_year != year:
        year_btn.click(by_js=True)
        target_year_btn = page.ele(
            f'x://tr[@class="oui-dt-calendar-year-column"]/td[@data-value="{year}" and not(contains(@class, "disabled-element"))]',
            timeout=3,
        )
        if not target_year_btn:
            raise RuntimeError(f'未找到年份 {year} 或该年份不可选')
        target_year_btn.click(by_js=True)

    month_btn = page.ele('c:span.oui-dt-calendar-control.month', timeout=3)
    if not month_btn:
        raise RuntimeError('未找到月份切换按钮')

    curr_month = month_btn.text.strip().rstrip('月')
    if curr_month != month:
        month_btn.click(by_js=True)
        target_month_btn = page.ele(
            f'x://tr[@class="oui-dt-calendar-month-column"]/td[text()="{month}月" and not(contains(@class, "disabled-element"))]',
            timeout=3,
        )
        if not target_month_btn:
            raise RuntimeError(f'未找到月份 {month} 或该月份不可选')
        target_month_btn.click(by_js=True)

    target_date_btn = page.ele(
        f't:td@@class^oui-dt-calendar-day@@data-value={date}', timeout=3
    )
    if not target_date_btn:
        raise RuntimeError(f'未找到日期 {date}')
    target_date_btn.click(by_js=True)

    page.ele('t:body').hover()


def get__shop_name(page: MixTab, throw_exception=True):
    """
    获取店铺名称

    Args:
        page: 页面对象, 默认为当前页面
        throw_exception: 出错时是否抛出异常, 默认为 True
    Returns:
        店铺名称
    """

    def find():
        target_value = None
        for key, value in page.local_storage().items():
            if 'PERSIST_DOMAIN|/portal/home.htm|店铺概况' not in key:
                continue
            target_value = value
            break
        else:
            raise ValueError('未找到包含店铺名称的本地存储数据的 Key')

        if not target_value:
            raise ValueError('本地存储数据 value 为空')
        target_value = parse__localstorage_data(target_value)
        if not isinstance(target_value, dict):
            raise ValueError('本地存储 value 格式非预期的 dict 类型')
        if 'levelInfo' not in target_value:
            raise ValueError('本地存储 value 中未找到 levelInfo 字段')
        level_info: dict = target_value.get('levelInfo')
        if not isinstance(level_info, dict):
            raise ValueError('本地存储 value.levelInfo 字段非预期的 dict 类型')
        shop_name: str = level_info.get('shopName')

        return shop_name

    shop_name = None
    try:
        shop_name = find()
    except Exception as e:
        if throw_exception is True:
            raise e

    return shop_name
