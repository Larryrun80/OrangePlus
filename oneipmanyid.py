#!/usr/bin/env python
# filename:oneipmanyid.py

from orangejuice.utils.orangemysql import OrangeMySQL

db_oneipmanyid_hanlder = OrangeMySQL('DB_ORANGE')


def forbid_user():
    addip = []
    querstring_user_addip = '''
        select u.addIp, count(u.uid) as count
        from murcielago_moneychange m,
        murcielago_user u
        where date_format(from_unixtime(m.addTime),'%Y-%m-%d') >
        date_sub(date(now()),interval 2 day)
        and date_format(from_unixtime(m.addTime),'%Y-%m-%d') < date(now())
        and m.uid=u.uid
        and m.remark='渠道送钱'
        and m.money=15
        group by u.addIp
        order by count desc
        limit 1000;
    '''
    result = db_oneipmanyid_hanlder.execute(querstring_user_addip)
    addip = result.fetchall()

    for (ip, count) in addip:
        if count >= 5:
            querstring_user_id = '''
                update murcielago_user
                set isForbidden=1
                where addIp = %s
                and date_format(from_unixtime(addTime),'%Y-%m-%d') >
                date_sub(date(now()),interval 2 day)
                and date_format(from_unixtime(addTime),'%Y-%m-%d') <
                date(now())
                ;
            '''
            db_oneipmanyid_hanlder.execute(querstring_user_id, ip)
            db_oneipmanyid_hanlder.commit()


forbid_user()

db_oneipmanyid_hanlder.close()
