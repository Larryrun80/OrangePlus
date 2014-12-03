#!/usr/bin/env python
#Filename: test.py

import sys
from orangejuice.utils.orangemail import OrangeMail
from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangecsv import OrangeCsv
from orangejuice.utils.orangelog import OrangeLog

# Mail example
# ============
# mailer = OrangeMail('MAIL_ORANGE');

# mailer.send_mail(
#                 ['guonan@doweidu.com',],
#                 'test',
#                 'this is a test from python',
#                 [sys.path[0] + '/README.md',]
#                 )

# MySQL example
# =============
# mysql_handler = OrangeMySQL('DB_ORANGE');
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
# logger = OrangeLog('LOG_ORANGE','test').getLogger()
# logger.info('test1 %s:%s','a','b')

# ======Orange Test============











