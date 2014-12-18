#!/usr/bin/env python
#Filename: dealwaitingpayment.py

import sys
from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangelog import OrangeLog

def get_not_dealed_wechat_orders():
    orders_to_deal_with = []
    querystring_get_wechat_error_order = '''
       SELECT id,
	      remark
         FROM Log_Order
        WHERE status = 19
     ORDER BY id DESC;
    '''
    # 取出所有状态为19 的订单
    result = db_wechat_handler.execute(querystring_get_wechat_error_order).fetchall()
    for (id, remark) in result:
      pos_start = remark.find('orderSn=')+8
      pos_end = remark.find('&amount')
      # 如果包含orderSn，则需要处理
      if (pos_start<pos_end):
          order_sn = remark[pos_start:pos_end]
          # 根据orderSn 取出订单
          order_info = get_order_info('sn', order_sn)
          if len(order_info) > 0:
              for (order_id, pool_id) in order_info:
                  if (order_id, pool_id) not in orders_to_deal_with:
                      orders_to_deal_with.append((order_id, pool_id))
      # 将其状态变更为190，表示已处理过
      change_log_status(id)
    return orders_to_deal_with

def change_log_status(id):
  querystring_set_status = '''
  UPDATE Log_Order
     SET status=190
   WHERE id = %s
  '''
  db_wechat_handler.execute(querystring_set_status, id)
  db_wechat_handler.commit()

def get_order_info(type, value):
    querystring_get_order_info = '''
       SELECT o.orderId, 
              se.poolId
         FROM murcielago_order o
    LEFT JOIN murcielago_goods_shop gs
           ON o.goodsId = gs.goodsId
    LEFT JOIN murcielago_goods g
           ON o.goodsId = g.goodsId
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

try:
  db_wechat_handler = OrangeMySQL('DB_WECHAT')
  db_orange_handler = OrangeMySQL('DB_ORANGE')
  db_ecode_handler = OrangeMySQL('DB_ECODE')

  # 取出需要处理的订单，包含oeder_id 和 pool_id 两列
  result = get_not_dealed_wechat_orders()
  if len(result) == 0:
      logger.info('Nothing Have to Deal With, Going To Sleep...')
  else:
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

except:
    logger.error('%s: %s', str(sys.exc_info()[0]), str(sys.exc_info()[1]))
