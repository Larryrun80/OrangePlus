#!/usr/bin/env python
#Filename: orangejuice/utils/orangemysql.py

import configparser
import mysql.connector
import os

class OrangeMySQL:
    ''' This Class is To Simplify Operate MySQL Databases. '''

    def __init__(self, section_name):
        # Read config file and init MySQL settings
        self._config_file = os.path.split(os.path.dirname(__file__))[0]
        self._config_file += '/conf/orangejuice.conf'
        config = configparser.ConfigParser()
        config.read(self._config_file)

        self.cnx = mysql.connector.connect(
            user=config.get(section_name,'User'),
            password=config.get(section_name,'Password'),
            host=config.get(section_name,'Host'),
            database=config.get(section_name,'Database')
            )
        self.cursor = self.cnx.cursor()

    def query(self, query, *args):
        # Check input data format
        if (not isinstance(query, str)):
            raise RuntimeError('Invalid Query: Must be a String!')

        self.cursor.execute(query, args)
        return self.cursor

    def execute(self, query, *args):
        # Check input data format
        if (not isinstance(query, str)):
            raise RuntimeError('Invalid Query: Must be a String!')
        self.cursor.execute(query, args)
        self.cursor.fetchone()


    def close(self):
        self.cnx.close()
