#!/usr/bin/env python
# Filename: statistics.py

import os
from datetime import date
from datetime import datetime
from datetime import timedelta

from orangejuice.utils.umeng import UmengHandler
from orangejuice.utils.orangemysql import OrangeMySQL

os.environ['TZ'] = 'Asia/Shanghai'


class Statistics():

    """
        Provides methodes to deal statistics issues
    """
    LEGAL_SOURCE = ('umeng', 'mysql')
    STAT_DB_SECTION = 'DB_STATISTICS'
    DATA_DB_SECTION = 'DB_DATASOURCE'
    UMENG_SECTION = 'UMENG_CONFIG'

    def __init__(self):
        self.stat_db = OrangeMySQL(self.STAT_DB_SECTION)
        self.umeng = None
        self.mysql = None
        return

    def get_available_events(self):
        sql_get_events = '''
                        SELECT      c.id `case_id`,
                                    c.case `case`,
                                    e.id `event_id`,
                                    e.event `event`,
                                    ds.source `data_source`,
                                    e.data_source_param `param`,
                                    e.data_source_value `value`,
                                    e.sql_str `sql_str`,
                                    c.start_date `start_date`,
                                    c.end_date `end_date`
                        FROM        `case` c
                        LEFT JOIN   `event` e ON e.case_id=c.id
                        LEFT JOIN   `data_source` ds ON e.data_source_id=ds.id
                        WHERE       c.start_date<now()
                        AND         (c.end_date>now() or c.end_date is null)
                        AND         c.enabled=1
                        ;
                        '''
        events = self.stat_db.execute(sql_get_events).fetchall()
        return events

    def get_value(self, source, param, event, sql_str, start_date, end_date):
        if ((not isinstance(source, str)) or
           (source.lower() not in self.LEGAL_SOURCE)):
            raise RuntimeError('Params Error: Not Legal Source')

        # get umeng data
        value = {}
        if source.lower() == 'umeng':
            if self.umeng is None:
                self.umeng = UmengHandler(self.UMENG_SECTION)

            value = self.umeng.get_event_data(self.umeng.appids[param],
                                              event, start_date, end_date)
        # get local database data
        elif source.lower() == 'mysql':
            if self.mysql is None:
                self.mysql = OrangeMySQL(self.DATA_DB_SECTION)

            # build result dictionary
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            delta_date = end_date - start_date
            for t_date in (start_date + timedelta(n)
                           for n in range(delta_date.days)):
                str_date = t_date.strftime('%Y-%m-%d')
                sql_str_exec = sql_str.format(str_date)
                sql_result = self.mysql.execute(sql_str_exec).fetchall()
                if len(sql_result) == 0:
                    value[str_date] = 0
                else:
                    value[str_date] = sql_result[0][0]
        return value

    def save_data(self, data):

        '''
        save data to statistics database
        '''
        sql_save_data = '''
                        INSERT INTO  `data`
                                    (`event_id`,
                                     `data_date`,
                                     `value`,
                                     `created_at`,
                                     `updated_at`)
                        VALUES
                        '''
        for (event_id, data_date, value) in data:
            sql_save_data += "({0}, '{1}', {2}, now(), now()),".format(
                                                                     event_id,
                                                                     data_date,
                                                                     value)
        sql_save_data = sql_save_data[0:-1]
        self.stat_db.execute(sql_save_data)
        self.stat_db.commit()

    def get_nearest_date(self, event_id):

        '''
        get event's nearest recorded date
        avoid to do duplicated work
        '''
        sql_get_date = '''
                       SELECT  MAX(`data_date`)
                       FROM    `data`
                       WHERE   `event_id` = {0}
                       ;
                       '''.format(event_id)
        nearest_date = self.stat_db.execute(sql_get_date).fetchall()
        if len(nearest_date) == 0:
            return None
        else:
            return nearest_date[0][0]


def main():
    stats = Statistics()
    events = stats.get_available_events()

    # for every event
    for (case_id, case, event_id, event, data_source,
         param, value, sql_str, start_date, end_date) in events:
        print("Dealing Case {case}[id: {case_id}] \
              -> Event {event}[id: {event_id}]".format(
                case=case,
                case_id=case_id,
                event=event,
                event_id=event_id))
        # get event's nearest recorded data
        # if its exists, substitute the start date to get data
        if stats.get_nearest_date(event_id) is not None:
            start_date = stats.get_nearest_date(event_id) +\
                timedelta(days=1)
        # deal end date
        if end_date is None:
            end_date = date.today()

        if end_date > start_date:
            # get data
            str_start_date = start_date.strftime('%Y-%m-%d')
            str_end_date = end_date.strftime('%Y-%m-%d')
            value = stats.get_value(data_source, param, value, sql_str,
                                    str_start_date, str_end_date)

            # insert to stat db
            insert_data = []
            delta_date = end_date - start_date
            for t_date in (start_date + timedelta(n)
                           for n in range(delta_date.days)):
                str_date = t_date.strftime('%Y-%m-%d')
                insert_data.append((event_id, str_date, value[str_date]))
            stats.save_data(insert_data)
        else:
            print('No Need To Work On Event {0}'.format(event))

if __name__ == '__main__':
    main()
