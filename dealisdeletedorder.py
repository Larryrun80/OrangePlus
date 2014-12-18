#!/user/bin/env python
# Filename: dealisdeletedorder.py

from orangejuice.utils.orangemysql import OrangeMySQL

db_deleted_handle = OrangeMySQL('DB_ORANGE')
db_confirmed_handle = OrangeMySQL('DB_ORANGE')

# 处理被删除订单
querystring_set_status = '''
    UPDATE murcielago_order
    SET deleted = 0
    WHERE dele ted = 1
    and orderStatus = 1
    and distributionNO is not null;
  '''
db_deleted_handle.execute(querystring_set_status)
db_deleted_handle.commit()
print('u save the orders!')

# 处理等待到账的订单
querystring_not_confirmed_order = '''
    select orderId
    from murcielago_order
    where payStatus=0
    and orderStatus = -2
    and distributionNO is not null;
    '''
result = db_confirmed_handle.execute(
    querystring_not_confirmed_order).fetchall()
print(result)

for (orderId,) in result:
    querystring_update_status = '''
        UPDATE murcielago_order
        SET orderStatus=1,
            payStatus=1
        WHERE orderId = %s
      '''
    db_confirmed_handle.execute(querystring_update_status, orderId)
    db_confirmed_handle.commit()
    print('orders confirmed now!')

db_deleted_handle.close()
