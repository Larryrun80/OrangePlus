#!/usr/bin/env python
# Filename: mysqldumper.py

###########################################################
#
# This python script is used for mysql database backup
# using mysqldump utility.
#
# Written by : Larry Guo
# Created date: June 29, 2015
# Last modified: June 29, 2015
# Tested with : Python 3.4.3
# Script Revision: 1.0
#
##########################################################

import os
import time

# MySQL database(s) settings, for backup
# Make sure below user have enough privileges
# To take multiple databases backup, write path of dbname file in DB_NAME
# and put databses names one on each line.
DB_HOST = 'localhost'
DB_USER = 'user'
DB_PASSWORD = 'password'
# DB_NAME = '/backup/dbs'
DB_NAME = 'db_name'
BACKUP_PATH = '/backup/dbbackup/'

# Getting current datetime to create backup folder like "20150629-071334".
DATETIME = time.strftime('%Y%m%d-%H%M%S')
TODAYBACKUPPATH = BACKUP_PATH + DATETIME

# Checking if backup folder already exists. Create it if not.
print("checking backup folder")
if not os.path.exists(TODAYBACKUPPATH):
    os.makedirs(TODAYBACKUPPATH)
    print('no folder found, created at {0}'.format(TODAYBACKUPPATH))
else:
    print('backup folder found')

# Checking if you want to take single database backup or multiple backups.
print("checking for databases names file.")
if os.path.exists(DB_NAME):
    multi = 1
    print("Databases file found...")
    print("Starting backup of all dbs listed in file " + DB_NAME)
else:
    print("Databases file not found...")
    print("Starting backup of database " + DB_NAME)
    multi = 0

# Starting actual database backup proceshaols.
if multi:
    db_file = open(DB_NAME, "r")
    file_length = len(db_file.readlines())

    for p in range(file_length):
        db = db_file.readline()   # reading database name from file
        db = db[:-1]         # deletes extra line
        dumpcmd = "mysqldump -u "\
                  + DB_USER\
                  + " -p"\
                  + DB_USER_PASSWORD\
                  + " "\
                  + db\
                  + " > "\
                  + TODAYBACKUPPATH\
                  + "/"\
                  + db\
                  + ".sql"
        os.system(dumpcmd)
    db_file.close()
else:
    db = DB_NAME
    dumpcmd = "mysqldump -u "\
              + DB_USER \
              + " -p" \
              + DB_USER_PASSWORD \
              + " " \
              + db \
              + " > " \
              + TODAYBACKUPPATH \
              + "/" \
              + db \
              + ".sql"
    os.system(dumpcmd)

print("Backup script completed")
print("Your backups has been created in '" + TODAYBACKUPPATH + "' directory")
