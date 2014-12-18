#!/usr/bin/env python
# Filename: orangejuice/utils/orangecsv.py

import csv
import os


class OrangeCsv:

    ''' This is a Class to Simplify Reading from & Writing to Excel files '''

    POSTFIX_LIST = ['csv', 'xls', 'xlsx', 'txt']

    def write(self, filename, data, encoder_list=['utf-8', ], operation='w'):
        # Check input data format
        if not isinstance(data, list):
            raise RuntimeError('Invalid Data, Should Pass a List!')
        if operation and not isinstance(operation, str):
            raise RuntimeError('Invalid Operation, Should Pass a String!')
        if not isinstance(filename, str):
            raise RuntimeError('Invalid File Name, Should Pass a String!')
        if not isinstance(encoder_list, list) and len(encoder_list) > 0:
            raise RuntimeError('Invalid  encoder_list, Should Pass a List!')

        filenames = []

        # Create File Name for Every encoder_list required
        dot_pos = filename.rfind('.')
        filename_prefix = filename_postfix = ''

        if dot_pos == -1:
            filename_prefix = filename
            filename_postfix = 'csv'
        else:
            filename_prefix = filename[:dot_pos]
            filename_postfix = filename.lower()[dot_pos+1:]
            if filename_postfix not in self.POSTFIX_LIST:
                raise RuntimeError('Not Valid FILE TYPE')

        for encode_name in encoder_list:
            name = filename_prefix + '_' + encode_name + '.' + filename_postfix
            filenames.append(name)
            self.create_file_with_data(name, data, encode_name, operation)

        return filenames

    # Create File if File is not Exists
    def create_file_with_data(self, filename,  data,  encoder,  operation):
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        if not os.path.isfile(filename):
            file = open(filename, 'w')
            file.close()

        # Write csv data
        target = open(filename, mode='w', encoding=encoder, errors='ignore')
        writer = csv.writer(target)
        writer.writerows(data)
