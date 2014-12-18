#!/usr/bin/env python
# filename: 45days.py

import sys
import time

from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangecsv import OrangeCsv
from orangejuice.utils.orangemail import OrangeMail

PERIOD = 45  # 查看距今n天后会到期的商户
FILENAME = sys.path[0] + '/backup/expiringmerchants_' + time.strftime("%Y%m%d", time.localtime()) + '.xls'
ENCODER = ['utf-8', 'gb18030']
RECIPIENTS = ['zhujue@doweidu.com', 'guonan@doweidu.com']
# now = int(time.time())


def get_expiring_merchants():
    # 取出所有即将到期的门店以及跟踪销售
    db_expiring_merchants_handler = OrangeMySQL('DB_ORANGE')
    querystring_shop_enddate = '''
        select s.shopId,s.shopName,seller.name,g.goodsName,max(g.endDate) as endDate
        from murcielago_shop s,
                   shop_seller ss,
                   seller,
                   murcielago_goods_shop gs,
                   murcielago_goods g
        where s.isHidden = 0
        and s.shopId = ss.shopId
        and ss.holderSellerId= seller.id
        and s.shopId = gs.shopId
        and gs.goodsId = g.goodsId
        and g.endDate > now()
        and g.endDate <= date_add(date(now()),interval %s day)
        and g.enable = 1
        group by shopId
        order by g.endDate desc
        ;
    '''
    result = db_expiring_merchants_handler.execute(
        querystring_shop_enddate, PERIOD).fetchall()
    db_expiring_merchants_handler.close()
    return result

# 生成csv文件


def generate_file(data):
    csv_handler = OrangeCsv()
    csv_file = FILENAME
    header = [('商户编号', '商户', '销售', '商品', '下线时间')]
    return csv_handler.write(csv_file, header + data, ENCODER)


def sent_email(attachments):
    mailer = OrangeMail('MAIL_ORANGE')
    mailer.send_mail(
        RECIPIENTS,
        '即将到期商户',
        '请查收附件',
        attachments
    )

expiring_merchants_data = get_expiring_merchants()
attachments = generate_file(expiring_merchants_data)
sent_email(attachments)
