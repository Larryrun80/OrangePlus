#!/usr/bin/env python
# filename: blockIp.py
import os
import sys
import subprocess as t

from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangelog import OrangeLog


def get_ips(mysql_handler, limit, block_count, white_list):
    sql_get_ip = '''
        select count(addIP) as count, addIp from murcielago_user
        where addTime>unix_timestamp('2015-01-09 17:00:00')
        group by addIp
        order by count(addIP) desc
        limit %s;
    '''
    result = mysql_handler.execute(sql_get_ip, limit).fetchall()
    ips_to_block = []
    for (count, addIp) in result:
        if (count > block_count) and (addIp not in white_list):
            ips_to_block.append(addIp)
    return ips_to_block


def read_ips(filename):
    blocked_ips = []
    if os.path.isfile(filename):
        f = open(filename)
        while True:
            the_line = f.readline()
            if len(the_line) == 0:
                break
            else:
                the_line = the_line.strip('\n')
                blocked_ips.append(the_line)
        f.close()
    return blocked_ips


def write_ips(filename, ips):
    f = open(filename, 'a')
    for ip in ips:
        f.write(ip + '\n')
    f.close()


def diff(a, b):
    return list(set(a) - set(b))


def block_ips(ips, logger):
    for ip in ips:
        cmd_txt = "iptables -I INPUT -s " + ip + " -j DROP"
        os.system(cmd_txt)
        logger.info('blocked ip: %s', ip)

SQL_LIMIT = 100
BLOCK_COUNT = 100
FILE_NAME = 'ips.bak'
WHITE_LIST = ('42.121.98.102', '42.121.98.110', '27.115.51.166')

try:
    logger = OrangeLog('LOG_ORANGE', 'blockip').getLogger()
    db_orange_handler = OrangeMySQL('DB_ORANGE')
    ips = get_ips(db_orange_handler, SQL_LIMIT, BLOCK_COUNT, WHITE_LIST)
    ips_exists = read_ips(FILE_NAME)
    ip_to_deal = diff(ips, ips_exists)
    write_ips(FILE_NAME, ip_to_deal)
    block_ips(ip_to_deal, logger)
except:
    logger.error('%s: %s', str(sys.exc_info()[0]), str(sys.exc_info()[1]))
