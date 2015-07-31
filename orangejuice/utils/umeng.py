#!/usr/bin/env python
# filename: orangejuice/utils/umeng.py

import os
import configparser

import requests


class UmengHandler:

    """
    This class try to get statistic data from umeng
    """

    def __init__(self, section_name='UMENG_CONFIG',
                 file_name='orangejuice.conf'):
        # build config file
        self._config_file = os.path.split(os.path.dirname(__file__))[0]
        self._config_file += '/conf/'
        self._config_file += file_name
        self.section_name = section_name

        # get configs
        config = configparser.ConfigParser()
        config.read(self._config_file)
        self.email = config.get(section_name, 'Email')
        self.password = config.get(section_name, 'Password')
        self.baseurl = config.get(section_name, 'BaseUrl')
        apps = {}
        self.appids = {}
        try:
            apps['Android'] = config.get(section_name, 'AppNameAndroid')
        except configparser.NoOptionError:
            print('Did Not Find Android App Name, Work on')
        try:
            apps['iOS'] = config.get(section_name, 'AppNameIOS')
        except configparser.NoOptionError:
            print('Did Not Find iOS App Name, Work on')

        if len(apps) == 0:
            print('No App assigned, Exit')
            return

        # authorize
        payload = {'email': self.email, 'password': self.password}
        r = requests.post(self.baseurl +
                          config.get(section_name, 'AuthrizeUrl'),
                          data=payload)
        if r.status_code == 200:
            jr = r.json()
            self.auth_token = jr['auth_token']
        else:
            print('{0} Error'.format(r.status_code))
            return
        self.params = {'auth_token': self.auth_token}

        # get app info
        r = requests.get(self.baseurl + config.get(section_name, 'AppsUrl'),
                         params=self.params)
        if r.status_code == 200:
            jr = r.json()
            for app_name in apps.keys():
                for app_info in jr:
                    if app_info['name'] == apps[app_name]:
                        self.appids[app_name] = app_info['appkey']
        else:
            print('{0} Error'.format(r.status_code))
            return

    def get_event_data(self, appid, event_name,
                       start_date, end_date, data_type='device'):

        '''
        Get Event's daily Data
        appid: umeng's appid
        envent_name: name of app's event
        start_date: the start date of the data
        end_date: the end date of data
        data_type: (device|count) device stands for unique user, and count
                    stands for total number
        '''
        # deal exception
        if len(self.appids) == 0:
            print('Can Not Find App in This Umeng Account!')
            return
        if ((not isinstance(start_date, str)) or
            (not isinstance(end_date, str)) or
            (appid is None) or
                (event_name is None)):
            print('Wrong Parameters.')
            return

        # build request params to get event id
        event_id = ''
        event_params = self.params
        event_params['appkey'] = appid
        event_params['start_date'] = start_date
        event_params['end_date'] = end_date
        event_params['period_type'] = 'daily'
        event_params['per_page'] = 10
        event_params['page'] = 1
        config = configparser.ConfigParser()
        config.read(self._config_file)
        group_url = self.baseurl + config.get(self.section_name, 'GroupUrl')
        find_event = False

        # find event
        while not find_event:
            r = requests.get(group_url, params=event_params)
            if r.status_code == 200:
                jr = r.json()
                for event in jr:
                    if event_name == event['name']:
                        find_event = True
                        event_id = event['group_id']
                event_params['page'] += 1
            else:
                print('{0} Error'.format(r.status_code))
                return

        # get event data and return
        return_data = {}
        if event_id == '':
            print('Event does not found')
            return
        event_params['group_id'] = event_id
        event_params['type'] = data_type
        r = requests.get(self.baseurl +
                         config.get(self.section_name, 'EventUrl'),
                         params=event_params)
        jr = r.json()
        for i in range(len(jr['dates'])):
            return_data[jr['dates'][i]] = jr['data']['all'][i]
        return return_data
