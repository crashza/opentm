#!/usr/bin/python

#
# OpenTM script to create rates from OpenTM DB
#
# Author Trevor Steyn <trevor@webon.co.za>
#

import csv
import time
import argparse
import progressbar
import mysql.connector
from config import *

################################### Defs ###########################################

def upload_destinations(file):
    accept_count = 0
    ignore_count = 0
    destinations = {}
    with open(file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[0] == "A":
                destinations[row[1]] = row[2]
                accept_count = accept_count + 1
            else:
                ignore_count = ignore_count + 1
    dbupdates = insert_destinations(destinations)
    print "summary:"
    print "%s commands accepted from csv %s ignored, %s db records updated/added" %(accept_count,ignore_count,dbupdates)
    return destinations


def insert_destinations(destinations):
    rows_updated    = 0
    cnx             = connect_db()
    cursor          = cnx.cursor()
    pbar            = progressbar.ProgressBar() 
    print "importing destinations standby.."
    for prefix in pbar(destinations):
        query = ''' INSERT into destinations
                    (prefix,i_group) SELECT '%s', g.i_group from groups g where name = '%s'
                    ON DUPLICATE KEY UPDATE i_group=g.i_group
                '''
        cursor.execute(query % (prefix,destinations[prefix]))
        cnx.commit()
        rows_updated = rows_updated + cursor.rowcount
    return rows_updated

def connect_db():
    cnx =  mysql.connector.connect(host=CFG_DB_HOST, user=CFG_DB_USER, password=CFG_DB_PASS, database=CFG_DB_DATABASE)
    return cnx

################################# End Defs #########################################

# Costants

CONST_VERSION = '0.1'

# parse CLI arguments

parser = argparse.ArgumentParser(description='OpenTM script');
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-d', '--destination', action='store_true', help='command to run')
group.add_argument('-v', '--vendor', action='store_true', help='command to run')
group.add_argument('-r', '--rates', type=str, help='command to run')
parser.add_argument('-f', '--file', type=str, help='file to process only usefull with -c destinations/vendors')
args = parser.parse_args()

if args.destination:
    upload_destinations(args.file)


