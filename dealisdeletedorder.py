#!/user/bin/env python
# -*- coding: utf-8 -*-
# Filename: dealisdeletedorder.py
import sys

from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangelog import OrangeLog


def deal_delete(db_handler, logger):
    sql_get_deleted = '''
    SELECT orderId
    FROM   murcielago_order
    WHERE  orderStatus=1
    AND    deleted=1
    AND    addTime>unix_timestamp('2015-01-08')
    '''
    result = db_handler.execute(sql_get_deleted).fetchall()
    print(result)
    sql_deal_deleted = '''
    UPDATE murcielago_order
    SET    deleted=0
    where  orderId=%s
    '''
    for (orderId,) in result:
        db_handler.execute(sql_deal_deleted, orderId)
        db_handler.commit()
        logger.info('dealed deleted order: %s', orderId)


try:
    db_handler = OrangeMySQL('DB_ORANGE')
    logger = OrangeLog('LOG_ORANGE', 'DelDealer').getLogger()
    deal_delete(db_handler, logger)
except:
    logger.error('%s: %s', str(sys.exc_info()[0]), str(sys.exc_info()[1]))
