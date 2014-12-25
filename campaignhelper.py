#!/usr/bin/env python
# Filename: campaignhelper.py

import os
import time
import sys

from orangejuice.utils.orangemysql import OrangeMySQL
from orangejuice.utils.orangelog import OrangeLog

STAUTS_TO_SCORE = 1
STATUS_UNREGISTED = 0
STATUS_REFISTED_ALREADY = 2


def get_undealed_mobiles(mysql_handler):
    sqlstr = '''
    select id, userid, mobile, created_at
    from cm_invate
    where (dealed is NULL
    or dealed = 0)
    and userid=543
    ;
    '''
    cursor = mysql_handler.execute(sqlstr)
    result = cursor.fetchall()
    return result


def confirm_list(mysql_handler, mobile_set):
    sqlstr = '''
    select addTime
    from murcielago_user
    where mobile = %s
    '''
    result = []
    for (sid, uid, mobile, register_time) in mobile_set:
        cursor = mysql_handler.execute(sqlstr, mobile)
        addTime = cursor.fetchone()
        if addTime is None:
            result.append(sid, uid, mobile, STATUS_UNREGISTED)
        elif addTime[0] > register_time.timestamp():
            result.append(sid, uid, mobile, STAUTS_TO_SCORE)
        else:
            result.append((sid, uid, mobile, STATUS_REFISTED_ALREADY))

    return result


def add_score(mysql_handler, deal_list, logger):
    sqlupdate = '''
    update cm_invate
    set dealed = %s
    where id = %s
    '''
    sqlscore = '''
    update christmas
    set gscore = gscore + 2000
    where userid = %s
    '''
    for (sid, uid, mobile, status) in deal_list:
        mysql_handler.execute(sqlupdate,  status, sid)
        logger.info('Dealed Invite ID: %s, Set Status to %s', sid, status)
        if status == STAUTS_TO_SCORE:
            mysql_handler.execute(sqlscore, uid)
            logger.info('Add Score to User %s,  \
                        With Invite ID %s, For recommand %s',
                        uid, sid, mobile)
        mysql_handler.commit()

# Setting TimeZone
os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

try:
    db_campaign_handler = OrangeMySQL('DB_EVENT')
    db_online_handler = OrangeMySQL('DB_ORANGE')
    logger = OrangeLog('LOG_ORANGE', 'Campaign').getLogger()

    list_step1 = get_undealed_mobiles(db_campaign_handler)
    list_step2 = confirm_list(db_online_handler, list_step1)
    add_score(db_campaign_handler, list_step2, logger)
    db_campaign_handler.close()
    db_online_handler.close()
except:
    logger.error('%s: %s', str(sys.exc_info()[0]), str(sys.exc_info()[1]))
