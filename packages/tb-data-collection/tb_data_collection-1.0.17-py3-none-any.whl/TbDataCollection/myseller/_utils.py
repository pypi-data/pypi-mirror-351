from DrissionPage._pages.mix_tab import MixTab


class Pagination:
    """分页器处理类"""

    @staticmethod
    def set__max_page_size(page: MixTab):
        """设置最大分页大小"""

        page_size_changer = page.ele('t:span@@text()=20条/页', timeout=8)
        if not page_size_changer:
            raise RuntimeError('未找到分页大小切换器')

        page_size_changer.scroll.to_see()
        page_size_changer.click(by_js=True)

        page_size_option = page.ele('t:span@@text()=100条/页', timeout=3)
        if not page_size_option:
            raise RuntimeError('未找到分页选项')

        page_size_option.click(by_js=True)

    @staticmethod
    def next_page(page: MixTab):
        """下一页"""

        arrow_ele = page.ele(f't:a@@class^mc-iconfont@@text()={chr(58882)}', timeout=3)
        if not arrow_ele:
            raise RuntimeError('未找到下一页按钮')

        if 'page' not in arrow_ele.attr('mx-click'):
            # 已经是最后一页
            return False

        arrow_ele.click(by_js=True)
        return True

    @staticmethod
    def prev_page(page: MixTab):
        """上一页"""

        arrow_ele = page.ele(f't:a@@class^mc-iconfont@@text()={chr(58900)}', timeout=3)
        if not arrow_ele:
            raise RuntimeError('未找到上一页按钮')

        if 'page' not in arrow_ele.attr('mx-click'):
            # 已经是第一页
            return False

        arrow_ele.click(by_js=True)
        return True
