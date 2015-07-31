#!/usr/bin/env python
# Filename: exportcase.py

import csv
import datetime
import sys

from orangejuice.utils.orangemysql import OrangeMySQL

STAT_DB_SECTION = 'DB_STATISTICS'

if __name__ == '__main__':
    # get input data
    case = input('Enter Case ID or Case Name:')
    get_date = False
    while(not get_date):
        try:
            start_date = input('Enter Start Date with Format YYYY-MM-DD:')
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            get_date = True
        except ValueError:
            print('Wrong Date Inputed')
    get_date = False
    while(not get_date):
        try:
            end_date = input('Enter End Date with Format YYYY-MM-DD:')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            if end_date > start_date:
                get_date = True
            else:
                print('End Date is Early Than Start Date')
        except ValueError:
            print('Wrong Date Inputed')

    print('Start Dealing Data...')
    # get events os case
    sql_events = 'SELECT c.case, e.id, e.event FROM `event` e \
                  INNER JOIN  `case` c on e.case_id = c.id WHERE '
    try:
        case = int(case)
        sql_events += 'c.id = ' + str(case)
    except ValueError:
        sql_events += "c.case = '{0}'".format(case)
    stat_db = OrangeMySQL(STAT_DB_SECTION)
    events = stat_db.execute(sql_events).fetchall()
    if len(events) == 0:
        print('No Events Found')
    else:
        # build output file
        file_name = "{path}/files/{case}-{date}.csv".format(
             path=sys.path[0],
             case=events[0][0],
             date=datetime.date.today().strftime('%Y%m%d'))
        csv_file = open(file_name, 'w')
        writer = csv.writer(csv_file)

        # write table header
        header = ['date']
        event_ids = []
        for (case, event_id, event) in events:
            header.append(event)
            event_ids.append(event_id)
        writer.writerow(header)

        # write data
        sql_data = '''
                   SELECT   `value`
                   FROM     `data`
                   WHERE    `event_id` = {0}
                   AND      date_format(`data_date`, '%Y-%m-%d') = '{1}'
                   '''
        delta_date = end_date - start_date
        for t_date in (start_date + datetime.timedelta(n)
                       for n in range(delta_date.days)):
            str_date = t_date.strftime('%Y-%m-%d')
            data = [str_date]
            for event_id in event_ids:
                sql_data_exec = sql_data.format(event_id, str_date)
                value = stat_db.execute(sql_data_exec).fetchall()
                if len(value) == 0:
                    data.append('')
                else:
                    data.append(value[0][0])
            writer.writerow(data)
        csv_file.close()
        print('Success Export Data to File: {0}'.format(file_name))
