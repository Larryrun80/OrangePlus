#!/usr/bin/env python
#Filename: orangejuice/utils/orangecsv.py

import csv
import os

class OrangeCsv:
    ''' This is a Class to Simplify Reading from & Writing to Excel files '''

    def write(self, filename, data, operation='w'):
        # Check input data format
        if not isinstance(data, list):
            raise RuntimeError('Invalid Data, Should Pass a List!')
        if operation and not isinstance(operation, str):
            raise RuntimeError('Invalid Operation, Should Pass a String!')
        if not isinstance(filename, str):
            raise RuntimeError('Invalid File Name, Should Pass a String!')

        # Create File if File is not Exists
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        if not os.path.isfile(filename):
            file = open(filename, 'w')
            file.close()

        # Write csv data
        with open(filename, operation) as f:
            writer = csv.writer(f)
            writer.writerows(data)