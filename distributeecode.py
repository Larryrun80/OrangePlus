#!/usr/bin/env python
# filename: distributeecode.py

import sys

from orangejuice.utils.orangemysql import OrangeMySQL


# 取验证码
ecodes = []
ecodes_file = sys.path[0] + '/ecode.csv'
file_source = open(ecodes_file, mode='r', encoding='utf-8')
while True:
    line = file_source.readline()
    ecodes.append(line.strip('\n'))
    if len(line) == 0:
        break
file_source.close()

db_ecode_handler = OrangeMySQL('DB_ORANGE')
db_disrtibuteecode_handler = OrangeMySQL('DB_ECODE')
# 找到码库
querystring_ecode_poolId = '''
    select se.poolId,
           s.shopId
    from murcielago_shop s,
         murcielago_shop_ecodepool se
    where s.isHidden = 0
    and s.shopId = se.shopId
    and se.isMultiShop = 0
    and s.parentId = 1877;
    '''

result = db_ecode_handler.execute(querystring_ecode_poolId).fetchall()
print(result)


# 清空码库里的验证码
for (poolId, shopId) in result:
    querystring_delete_all_records = 'TRUNCATE TABLE p%s;'
    db_disrtibuteecode_handler.execute(querystring_delete_all_records, poolId)
    db_disrtibuteecode_handler.commit

# 添加新的验证码
    for j in  range(0,55):
        querystring_add_records = 'insert into p' + str(poolId) + ' values (%s, 0)'
        db_disrtibuteecode_handler.execute(querystring_add_records, ecodes.pop(0))
        db_disrtibuteecode_handler.commit
        j=j+1

db_ecode_handler.close()
db_disrtibuteecode_handler.close()
