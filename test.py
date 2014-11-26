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
# mailer.send_mail('zhujue@doweidu.com',
#                 ['zhujue@doweidu.com',],
#                 'test',
#                 'this is a test from python',
#                 [sys.path[0] + '/README.md',])

# MySQL example
# =============
# mysql_handler = OrangeMySQL();
# result = mysql_handler.execute(
#     'select uid, mobile, money from murcielago_user WHERE uid > %s limit 3;',
#     [1000,]
#     )
# for (uid, mobile, money) in result:
#     print(uid, mobile, money)
# mysql_handler.close()

# CSV file example
# ================
# csv_handler = OrangeCsv(sys.path[0] + '/test.csv')
# header = [('col1', 'col2', 'col3')]
# data = [(1,2,3),('a','b','c'),(4,6,8)]
# csv_handler.write(data)
# csv_handler.write(header+data)
# csv_handler.write(data,'a')

# Log example
# ===========
# logger = OrangeLog('test').getLogger()
# logger.info('test1 %s:%s','a','b')

# ======Orange Test============

