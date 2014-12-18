#!/usr/bin/env python
#Filename: orangejuice/utils/orangelog.py

import logging
import configparser
import os
import sys
import time


class OrangeLog:

    ''' This is a Class to Simplify Loggine issues. '''

    def __init__(self, section_name, name=''):
        # You can pass a name to build your log file path
        # Setting TimeZone
        os.environ['TZ'] = 'Asia/Shanghai'
        time.tzset()

        # Read config file and init MySQL settings
        self._config_file = os.path.split(os.path.dirname(__file__))[0]
        self._config_file += '/conf/orangejuice.conf'
        config = configparser.ConfigParser()
        config.read(self._config_file)
        self.name = name

        # Build File Path String
        if config.get(section_name, 'Type') == 'Dynamic':
            if name != '':
                sep = '-'
            else:
                sep = ''
            self.log_path = sys.path[0] \
                + config.get(section_name, 'Dir') \
                + name \
                + sep \
                + time.strftime(config.get(section_name,
                                           'DynamicPart')) \
                + '.log'
        elif config.get(section_name, 'Type') == 'Static':
            if name == '':
                name = 'orange'
            self.log_path = sys.path[0] \
                + config.get(section_name, 'Dir') \
                + name \
                + '.log'
        else:
            raise RuntimeError('Invalid Log File Type set in Config File,'
                               ' Must be "Dynamic" or "Static"')

        if not os.path.exists(os.path.dirname(self.log_path)):
            os.makedirs(os.path.dirname(self.log_path))

        # Do basic config settings
        logging.basicConfig(
            level=logging.NOTSET,
            filename=self.log_path,
            format=config.get(section_name, 'Format'),
            filemode='a',
            )

    def getLogger(self):
        return logging.getLogger(self.name)
