#!/usr/bin/env python
# filename: 45days.py

import sys
import time

from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangecsv import OrangeCsv
from orangejuice.utils.orangemail import OrangeMail

days = 45  # 查看距今n天后会到期的商户
# now = int(time.time())


def get_expiring_merchants():
    # 取出所有即将到期的门店以及跟踪销售
    db_expiring_merchants_handler = OrangeMySQL('DB_ORANGE')
    querystring_shop_enddate = '''
        select s.shopId,s.shopName,seller.name,g.goodsName,max(g.endDate) as endDate
        from murcielago_shop s,shop_seller ss, seller, murcielago_goods_shop gs, murcielago_goods g
        where s.isHidden = 0
        and s.shopId = ss.shopId
        and ss.holderSellerId= seller.id
        and s.shopId = gs.shopId
        and gs.goodsId = g.goodsId
        and g.endDate > now()
        and g.endDate <= date_add(date(now()),interval %s day)
        and g.enable = 1
        and g.`isMultiShop`= 0
        group by shopId
        order by g.endDate desc
        ;
    '''
    result = db_expiring_merchants_handler.execute(
        querystring_shop_enddate, days).fetchall()
    db_expiring_merchants_handler.close()
    return result

# 生成csv文件


def generate_file_csv():
    csv_handler = OrangeCsv()
    csv_file = sys.path[0] + '/backup/expiringmerchants_utf8_' + \
        time.strftime("%Y%m%d", time.localtime()) + '.csv'
    header = [('商户编号', '商户', '销售', '商品', '下线时间')]
    data = expiring_merchants_list
    csv_handler.write(csv_file, header + data)
    return csv_file


def generate_files_ansi():
    # 将utf8转换成ansi
    file_test_ansi = sys.path[
        0] + '/backup/expiringmerchants_' + time.strftime("%Y%m%d", time.localtime()) + '.xls'

    # open and encode the original content
    file_source = open(csv_file, mode='r', encoding='utf-8', errors='ignore')
    file_content = file_source.read()
    file_source.close()

    # write the UTF8 file with the encoded content
    file_target = open(
        file_test_ansi, mode='w', encoding='gb18030', errors='ignore')
    file_target.write(file_content)
    file_target.close()
    return file_test_ansi


def sent_email():
    mailer = OrangeMail('MAIL_ORANGE')
    mailer.send_mail(
        ['zhujue@doweidu.com', 'lianjianping@doweidu.com'],
        '即将到期商户',
        '请查收附件',
        [ansi_file, csv_file]
    )

expiring_merchants_list = get_expiring_merchants()
csv_file = generate_file_csv()
ansi_file = generate_files_ansi()
sent_email()
