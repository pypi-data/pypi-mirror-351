class Report:
    star_shop__overview = {
        '消耗': 'cost',
        '搜索访客数': 'requestUvHllc',
        '搜索量': 'requestCnt',
        '展现量': 'impression',
        '自然流量增量曝光': 'searchimpression',
        '点击单价': 'cpc',
        '点击率': 'ctr',
        '点击量': 'click',
        '跳转点击单价': 'shopcpc',
        '店铺收藏数': 'favshoptotal',
        '宝贝收藏数': 'favitemtotal',
        '宝贝加购数': 'carttotal',
        '行动访客数': 'actionUvHllc',
        '店铺收藏访客数': 'shop_fav_uv',
        '转化率': 'cpt_cvr',
        '回报率': 'roi',
        '成交笔数': 'transactionshippingtotal',
        '成交金额': 'transactiontotal',
        '自然流量增量成交': 'searchtransactiontotal',
        '访客触达率': 'uvRate',
        '搜索进店率': 'shopUvRate',
        '进店行动率': 'actionUvRate',
        '行动成交率': 'actionCloseRate',
    }


class Dictionary:
    report = Report()
