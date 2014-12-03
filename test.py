#!/usr/bin/env python
#Filename: test.py

import sys
from orangejuice.utils.orangemail import OrangeMail
from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangecsv import OrangeCsv
from orangejuice.utils.orangelog import OrangeLog

# Mail example
# ============
# mailer = OrangeMail();

# mailer.send_mail(
#                 ['guonan@doweidu.com',],
#                 'test',
#                 'this is a test from python',
#                 [sys.path[0] + '/README.md',]
#                 )

# MySQL example
# =============
# mysql_handler = OrangeMySQL();
# result = mysql_handler.execute(
#     'select * from murcielago_user WHERE uid > %s limit %s;',
#     1000,
#     5
#     )
# print(result.fetchall())
# mysql_handler.close()

# CSV file example
# ================
# csv_handler = OrangeCsv()
# csv_file = sys.path[0] + '/test.csv'
# header = [('col1', 'col2', 'col3')]
# data = [(1,2,3),('a','b','c','d')]
# csv_handler.write(csv_file, data)
# csv_handler.write(csv_file, header+data)
# csv_handler.write(csv_file, data,'a')


# Log example
# ===========
# logger = OrangeLog('test').getLogger()
# logger.info('test1 %s:%s','a','b')

# ======Orange Test============
db_orange_handler = OrangeMySQL('DB_ORANGE')
db_ecode_handler = OrangeMySQL('DB_ECODE')

# 取出Order Id, Pool Id
querystring_get_pool = '''
            select o.orderId, g.`isMultiShop` g_flag, se.`isMultiShop` se_flag, se.`poolId`
            from murcielago_order o
            left join murcielago_goods_shop gs
            on o.goodsId=gs.goodsId
            left join murcielago_goods g
            on o.goodsId=g.goodsId
            left join `murcielago_shop_ecodepool` se
            on gs.shopId = se.shopId
            where o.orderStatus = -2;
            '''
result = db_orange_handler.query(querystring_get_pool)

# 取出当前活动对应的通兑／非通兑库id
pool_id =0
order_id =0
for tmp_order_id, g_flag, se_flag, tmp_pool_id in result:
    if g_flag == se_flag:
        pool_id = tmp_pool_id
        order_id = tmp_order_id

        if pool_id==0 or order_id ==0:
            raise RuntimeError('error')

        print(pool_id)
        print(order_id)

        # 更新一个可用的验证码状态，并取出这个验证码
        # TODO: 更新验证码使用状态
        querystring_get_ecode = '''
                        select ecode
                        from p%s
                        where isUsed = 0
                        limit 1;
                        '''
        ecode = db_ecode_handler.query(querystring_get_ecode, pool_id).fetchall()[0][0];
        querystring_set_ecode_status = '''
                        update p%s
                        set isUsed = 1
                        where ecode =%s
                        and isUsed = 0;
                        '''
        db_ecode_handler.execute(querystring_set_ecode_status, pool_id, ecode)
        db_ecode_handler.cnx.commit()
        print(ecode)
        db_ecode_handler.close()

        # 更新订单
        querystring_update_order = '''
                        update murcielago_order
                        set `distributionNo` = %s,
                        orderStatus = 1,
                        `payStatus` = 1
                        where orderId =%s ;
                        '''

        db_orange_handler.execute(querystring_update_order, ecode, order_id)
        db_orange_handler.cnx.commit()

        # 验证
        query = '''
            select orderId, payStatus, orderStatus, distributionNo
            from murcielago_order
            where orderId = %s;
            '''
        print(db_orange_handler.query(query, order_id).fetchall())

# result = mysql_handler.query(
#     '''select orderId, payStatus
#     from murcielago_order
#     WHERE orderStatus=%s
#     and distributionNo is null;''',
#     -2,
#     )
# order=result.fetchall()
# print(order)

# mysql_handler.execute(
#     '''update murcielago_order
#     set payStatus=1
#     WHERE orderStatus=%s
#     and distributionNo is null;''',
#     -2
#     )

# mysql_handler.cnx.commit()
# print('done')
#print(update.fetchall())

db_orange_handler.close()








