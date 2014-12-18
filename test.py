#!/usr/bin/env python
# Filename: test.py

import sys

from orangejuice.utils.orangemail import OrangeMail
# from orangejuice.utils.orangemysql import OrangeMySQL
# from orangejuice.utils.orangecsv import OrangeCsv
# from orangejuice.utils.orangelog import OrangeLog

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
def generate_file_csv():
    csv_handler = OrangeCsv()
    file_csv = sys.path[0] + '/test_utf8.csv'
    header = [('col1', 'col2', 'col3')]
    data = [(1, 2, 3), ('a', 'b', 'c'), ('一', '二')]
    csv_handler.write(csv_file, header + data)
    csv_handler.write(csv_file, data, 'a')
    return file_csv


def genearte_files_ansi():
# 将utf8转换成ansi
    file_test_ansi = sys.path[0] + "/files/test_ansi.xls"

# open and encode the original content
    file_source = open(csv_file, mode='r', encoding='utf-8', errors='ignore')
    file_content = file_source.read()
    file_source.close()

# write the UTF8 file with the encoded content
    file_target = open(file_test_ansi, mode='w', encoding='gbk')
    file_target.write(file_content)
    file_target.close()
    return file_test_ansi

csv_file = generate_file_csv()
ansi_file = genearte_files_ansi()

mailer = OrangeMail('MAIL_ORANGE')
mailer.send_mail(
    ['zhujue@doweidu.com', ],
    'test',
    'this is a test from python',
    [ansi_file]
)
