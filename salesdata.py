#!/usr/bin/env python
#filename: salesdata.py

import sys
import time

from orangejuice.utils.orangecsv import OrangeCsv
from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangemail import OrangeMail

FILENAME = sys.path[0] + '/salesdata.xls'
ENCODER = ['utf-8', 'gb18030']
RECIPIENTS = ['zhujue@doweidu.com']
db_salesdata_handler = OrangeMySQL('DB_ORANGE')

def get_shop_goods_date():
    querstring_shop_goods = '''
        select s.shopId,
               s.shopName,
               g.goodsId,
               g.goodsName
        from murcielago_shop s,
             murcielago_goods_shop gs,
             murcielago_goods g
        where s.shopId=gs.shopId
          and gs.goodsId=g.goodsId
          and s.cityId=21
          and g.endDate>'2013-12-31'
          order by s.shopId
          ;
    '''

    sg_cursor = db_salesdata_handler.execute(querstring_shop_goods)
    sgdata = sg_cursor.fetchall()
    sg_cursor.close()
    return sgdata

def get_order_date(sgdata):
    result = []
    for (shopId, shopName, goodsId, goodsName) in sgdata:
        head = [shopName, goodsName]
        temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        querstring_orders = '''
            select count(o.orderId),
                   sum(o.payPrice),
                   date_format(from_unixtime(o.addTime),'%m') as addTime
            from murcielago_order o,
                 murcielago_order_goods og
            where o.orderId=og.orderId
              and (o.orderStatus=1 or o.orderStatus=2)
              and o.addTime>unix_timestamp('2014-01-01 00:00:00')
              and og.goodsId=%s
              group by addTime;
        '''
        o_cursor = db_salesdata_handler.execute(querstring_orders, goodsId)
        odata = o_cursor.fetchall()
        o_cursor.close()
        if len(odata) > 0:
            for (c, p, m) in odata:
                temp[(int(m)-1)*2] = c
                temp[(int(m)-1)*2+1] = p
            result.append(head + temp)
        # time.sleep(2)
        # print('wait~~')
    print(result)
    return result


def generate_file(data):
    csv_handler = OrangeCsv()
    csv_file = FILENAME
    header = [('商户名称', '商品名称', '1月订单量', '1月销售额',
               '2月订单量', '2月销售额', '3月订单量', '3月销售额',
               '4月订单量', '4月销售额', '5月订单量', '5月销售额',
               '6月订单量', '6月销售额', '7月订单量', '7月销售额',
               '8月订单量', '8月销售额', '9月订单量', '9月销售额',
               '10月订单量', '10月销售额', '11月订单量', '11月销售额',
               '12月订单量', '12月销售额')]
    return csv_handler.write(csv_file, header + data, ENCODER)

def sent_email(attachments):
    mailer = OrangeMail('MAIL_ORANGE')
    mailer.send_mail(
        RECIPIENTS,
        '2014年商户订单统计',
        '请查收附件',
        attachments
    )
# get_shop_goods_date()
expiring_shop_goods_data = get_shop_goods_date()
expiring_orders_data = get_order_date(expiring_shop_goods_data)
attachments = generate_file(expiring_orders_data)
sent_email(attachments)

db_salesdata_handler.close()
