#!/usr/bin/env python
#Filename: dealwaitingpayment.py

import sys
from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangelog import OrangeLog

def not_dealed_wechat_orders():
    orders_to_deal_with = []
    querystring_get_wechat_error_order = '''
       SELECT id,
	      remark
         FROM Log_Order
        WHERE status = 19
     ORDER BY id DESC
        LIMIT 40;
    '''
    result = db_wechat_handler.execute(querystring_get_wechat_error_order).fetchall()
    for (id, remark) in result:
        pos_start = remark.find('orderSn=')+8
        pos_end = remark.find('&amount')
        if (pos_start<pos_end):
            order_sn = remark[pos_start:pos_end]
            order_info = get_order_info('sn', order_sn)
            if len(order_info) == 0:
                logger.info('Nothing to do')
            else:
                logger.info('-------Dealed Sn: %s-------', order_sn)
                for (order_id, pool_id) in order_info:
                    orders_to_deal_with.append((order_id, pool_id))
    return orders_to_deal_with

def get_order_info(type, value):
    querystring_get_order_info = '''
       SELECT o.orderId, 
              se.poolId
         FROM murcielago_order o
    LEFT JOIN murcielago_goods_shop gs
           ON o.goodsId = gs.goodsId
    LEFT JOIN murcielago_goods g
           ON o.goodsId=g.goodsId
    LEFT JOIN murcielago_shop_ecodepool se
           ON gs.shopId = se.shopId
        WHERE g.isMultiShop = se.isMultiShop
    '''
    if type=='sn':
        querystring_get_order_info = querystring_get_order_info +\
        '''
          AND o.orderSn = %s
          AND o.orderStatus in (-2,-1,0)
        '''
    if type=='status':
        querystring_get_order_info = querystring_get_order_info +\
        ' AND o.orderStatus = %s'
    return db_orange_handler.execute(querystring_get_order_info, value).fetchall()

def get_waiting_confirm_orders():
    querystring_get_pool = '''
       SELECT o.orderId, 
              se.poolId
         FROM murcielago_order o
    LEFT JOIN murcielago_goods_shop gs
           ON o.goodsId = gs.goodsId
    LEFT JOIN murcielago_goods g
           ON o.goodsId=g.goodsId
    LEFT JOIN murcielago_shop_ecodepool se
           ON gs.shopId = se.shopId
        WHERE o.orderStatus = -2
          AND g.isMultiShop = se.isMultiShop;
    '''
    return db_orange_handler.execute(querystring_get_pool).fetchall()

def find_distirbution_no(pool_id):
    querystring_get_ecode = '''
    SELECT ecode
      FROM p%s
     WHERE isUsed = 0
     LIMIT 1;
    '''
    ecode = db_ecode_handler.execute(querystring_get_ecode, pool_id).fetchall()[0][0];
    querystring_set_ecode_status = '''
    UPDATE p%s
       SET isUsed = 1
     WHERE ecode =%s
       AND isUsed = 0;
    '''
    db_ecode_handler.execute(querystring_set_ecode_status, pool_id, ecode)
    db_ecode_handler.commit()
    return ecode

def update_order(order_id, ecode):
    querystring_update_order = '''
    UPDATE murcielago_order
       SET distributionNo = %s,
           orderStatus = 1,
           payStatus = 1
     WHERE orderId =%s ;
    '''
    result = db_orange_handler.execute(querystring_update_order, ecode, order_id)
    db_orange_handler.commit()

    # 验证
    query = '''
    SELECT orderId, 
           payStatus, 
           orderStatus, 
           distributionNo
      FROM murcielago_order
     WHERE orderId = %s;
    '''
    # print('Done! Order is Now: \n{0}'.format(db_orange_handler.execute(query, order_id).fetchall()))

logger = OrangeLog('LOG_ORANGE', 'WP_Order').getLogger()
logger.info('=======Start Working=======')

db_wechat_handler = OrangeMySQL('DB_WECHAT')
db_orange_handler = OrangeMySQL('DB_ORANGE')
db_ecode_handler = OrangeMySQL('DB_ECODE')
result = not_dealed_wechat_orders()
if len(result) == 0:
    logger.info('Nothing Have to Deal With, Going To Sleep...')
else:
    # 取出当前活动对应的通兑／非通兑库id
    for (order_id, pool_id) in result:
        logger.info('Dealing With Order: %s, Which With Pool %s', order_id, pool_id)
        # 更新一个可用的验证码状态，并取出这个验证码
        ecode = find_distirbution_no(pool_id)
        logger.info('Dealing With Order: %s, Using Distribution No %s', order_id, ecode)
        # 更新订单
        update_order(order_id, ecode)
        logger.info('-------Dealed Order: %s-------', order_id)

db_orange_handler.close()
db_ecode_handler.close()
# logger = OrangeLog('LOG_ORANGE', 'WP_Order').getLogger()
# logger.info('=======Start Working=======')

# try:
#     db_orange_handler = OrangeMySQL('DB_ORANGE')
#     db_ecode_handler = OrangeMySQL('DB_ECODE')
#     db_wechat_handler = OrangeMySQL('DB_WECHAT')

#     # 找到-2状态订单
#     result = get_waiting_confirm_orders()
#     if len(result) == 0:
#         logger.info('Nothing Have to Deal With, Going To Sleep...')
#     else:
#         # 取出当前活动对应的通兑／非通兑库id
#         for (order_id, pool_id) in result:
#             logger.info('Dealing With Order: %s, Which With Pool %s', order_id, pool_id)
#             # 更新一个可用的验证码状态，并取出这个验证码
#             ecode = find_distirbution_no(pool_id)
#             logger.info('Dealing With Order: %s, Using Distribution No %s', order_id, ecode)
#             # 更新订单
#             update_order(order_id, ecode)
#             logger.info('-------Dealed Order: %s-------', order_id)

#     db_orange_handler.close()
#     db_ecode_handler.close()

# except:
#     logger.error('%s: %s', str(sys.exc_info()[0]), str(sys.exc_info()[1]))
