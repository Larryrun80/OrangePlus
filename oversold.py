#!/usr/bin/env python
# filename:oversold.py

from orangejuice.utils.orangemysql import OrangeMySQL
# from orangejuice.utils.orangemail import OrangeMail

db_comparegswithsv_hanlder = OrangeMySQL('DB_ORANGE')


def get_goodsstocks():
    # 取得前日在线商品的库存数
    stocks = []
    querstring_goods_data = '''
        select goodsId,
               goodsStocks
        from murcielago_goods
        where beginDate<=date_sub(CURDATE(),interval 1 day)
              and endDate>=date_sub(CURDATE(),interval 1 day)
              and enable='1'
              order by goodsId
              limit 1000
        ;
    '''
    result = db_comparegswithsv_hanlder.execute(querstring_goods_data)
    stocks = result.fetchall()
    # print(stocks)
    return stocks


def get_sealsvolume(stocks):
    # 统计前日售出商品的数量
    salesvolume = []
    querstring_order_data = '''
        select og.goodsId ,count(o.orderId) as volume
        from murcielago_order o ,murcielago_order_goods og
        where orderStatus in (1 ,2)
        and o.orderId=og.orderId
        and DATE_FORMAT(from_unixtime(o.addTime),'%Y-%m-%d')=
            date_sub(CURDATE() ,interval 1 day)
        group by og.goodsId
        order by og.goodsId
        limit 1000
        ;
    '''
    order = db_comparegswithsv_hanlder.execute(querstring_order_data)
    salesvolume = order.fetchall()
    # print(salesvolume)
    return salesvolume

    for (goodsId, stocks) in stocks:
        if goodsId == og.goodsId:
            stocks－volume

# 如果售出数>库存数，发邮件通知


db_comparegswithsv_hanlder.close()
