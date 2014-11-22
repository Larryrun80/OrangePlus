#!/usr/bin/env python
#Filename: orangejuice/utils/orangecsv.py

import csv
import os

class OrangeCsv:
    ''' This is a Class to Simplify Reading from & Writing to Excel files '''

    def __init__(self, file):
        self.csv_file = file

    def write(self, data, operation='w'):
        # Check input data format
        if not isinstance(data, list):
            raise RuntimeError('Invalid Data, Should Pass a List!')
        if operation and not isinstance(operation, str):
            raise RuntimeError('Invalid Operation, Should Pass a String!')

        if not os.path.exists(os.path.dirname(self.csv_file)):
            os.makedirs(os.path.dirname(self.csv_file))

        if not os.path.isfile(self.csv_file):
            file = open(self.csv_file, 'w')
            file.close()

        with open(self.csv_file, operation) as f:
            writer = csv.writer(f)
            writer.writerows(data)