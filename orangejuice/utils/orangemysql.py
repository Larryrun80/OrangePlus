#!/usr/bin/env python
# Filename: orangejuice/utils/orangemysql.py

import configparser
import os

import mysql.connector


class OrangeMySQL:

    ''' This Class is To Simplify Operate MySQL Databases. '''

    def __init__(self, section_name):
        # Read config file and init MySQL settings
        self._config_file = os.path.split(os.path.dirname(__file__))[0]
        self._config_file += '/conf/orangejuice.conf'
        config = configparser.ConfigParser()
        config.read(self._config_file)

        self.cnx = mysql.connector.connect(
            user=config.get(section_name, 'User'),
            password=config.get(section_name, 'Password'),
            host=config.get(section_name, 'Host'),
            database=config.get(section_name, 'Database'),
            port=config.get(section_name, 'Port'),
            connection_timeout=600,
            buffered=True
            )
        self.cursor = self.cnx.cursor()

    def execute(self, query, *args):
        # Check input data format
        if (not isinstance(query, str)):
            raise RuntimeError('Invalid Query: Must be a String!')
        self.cursor.execute(query, args)
        return self.cursor

    def executemany(self, query, data):
        # Check input data format
        if (not isinstance(query, str)):
            raise RuntimeError('Invalid Query: Must be a String!')
        if (not isinstance(data, list)):
            raise RuntimeError('Invalid Data: Must be a List!')
        self.cursor.executemany(query, data)

    def commit(self):
        self.cnx.commit()

    def close(self):
        self.cnx.close()

    def get_cnx(self):
        return self.cnx
