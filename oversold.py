#!/usr/bin/env python
# filename:oversold.py

from orangejuice.utils.orangemysql import OrangeMySQL
# from orangejuice.utils.orangemail import OrangeMail

db_stocksnumbers_hanlder = OrangeMySQL('DB_ORANGE')


# 取得当日在线商品的库存数
def get_online_goods_data():
    stocks = []
    querstring_goods_stocks = '''
        select goodsId,
               goodsStocks
        from murcielago_goods
        where beginDate<=date_sub(CURDATE(),interval 1 day)
              and endDate>=date_sub(CURDATE(),interval 1 day)
              and enable='1'
              limit 1000
        ;
    '''
    result = db_stocksnumbers_hanlder.execute(querstring_goods_stocks)
    stocks = result.fetchall()
    print(stocks)
    return stocks


# 统计当日售出商品的数量
def get_order_data():
    numbers = []
    querstring_sold_numers = '''
        select og.goodsId ,count(o.orderId)
        from murcielago_order o ,murcielago_order_goods og
        where orderStatus in (1 ,2)
        and o.orderId=og.orderId
        and DATE_FORMAT(from_unixtime(o.addTime),'%Y-%m-%d') =
            date_sub(CURDATE() ,interval 1 day)
        group by og.goodsId
        limit 1000
        ;
    '''
    order = db_stocksnumbers_hanlder.execute(querstring_sold_numers)
    numbers = order.fetchall()
    print(numbers)
    return numbers

# 将两个数字进行比较


# 如果售出数>库存数，发邮件通知

get_online_goods_data()
get_order_data()

db_stocksnumbers_hanlder.close()
