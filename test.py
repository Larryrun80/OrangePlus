#!/usr/bin/env python
#Filename: test.py

import sys
from orangejuice.utils.orangemail import OrangeMail
from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangecsv import OrangeCsv

# Mail example
# ============
# mailer = OrangeMail();
# mailer.send_mail('guonan@doweidu.com', 
#                 ['guonan@doweidu.com',], 
#                 'test', 
#                 'this is a test from python',
#                 [sys.path[0] + '/README.md',])

# MySQL example
# =============
# mysql_handler = OrangeMySQL();
# result = mysql_handler.execute(
    # 'select * from murcielago_user WHERE uid > %s limit 3;', 
    # [1000,]
    # )
# print(result.fetchall())

# CSV file example
# ================
# csv_handler = OrangeCsv(sys.path[0] + '/test.csv')
# header = [('col1', 'col2', 'col3')]
# data = [(1,2,3),('a','b','c')]
# csv_handler.write(data)
# csv_handler.write(header+data)
# csv_handler.write(data,'a')
