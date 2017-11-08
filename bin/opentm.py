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

def add_vendor():
    vendor      = raw_input("enter vendor name:")
    description = raw_input("enter vednor desription:")
    cnx             = connect_db()
    cursor          = cnx.cursor()
    query = 'INSERT into vendors (name,description) VALUES(\'%s\',\'%s\')' % (vendor,description)
    cursor.execute(query)
    cnx.commit()
    print "done"



def upload_vendor_rates(file,vendor):
    # TODO compare existing to upload and delete if full rate is selcted
    accept_count = 0
    ignore_count = 0
    vendor_rates = {}
    with open(file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[0] == "A":
                accept_count = accept_count + 1
                vendor_rates[row[1]] = row[2]
            else:
                ignore_count = ignore_count + 1
    dbupdates = insert_vendor_rates(vendor_rates,vendor)
    print "summary:"
    print "\t%s commands accepted from csv\n\t%s commands ignored from csv\n\t%s db records updated/added" %(accept_count,ignore_count,dbupdates)


def insert_vendor_rates(vendor_rates,vendor):
    rows_updated    = 0
    cnx             = connect_db()
    cursor          = cnx.cursor()
    pbar            = progressbar.ProgressBar()

    query = 'SELECT i_vendor from vendors where name=\'%s\'' % vendor
    cursor.execute(query)
    i_vendor = 'none'
    for i_vendor in cursor:
        i_vendor =  i_vendor[0]
    if  cursor.rowcount != 1:
        print "unkown vendor %s" % vendor
        exit()
    print "importing vendor rates standby.."
    for prefix in pbar(vendor_rates):
        query = '''INSERT into vendor_rates 
                   (i_destination,i_vendor,price,status) 
                   SELECT d.i_destination, '%s', '%s' ,'O' from destinations d 
                   where prefix = '%s' ON DUPLICATE KEY UPDATE 
                   price=%s, status='O';
                '''
        cursor.execute(query % (i_vendor, vendor_rates[prefix], prefix,vendor_rates[prefix]))
        cnx.commit()
        rows_updated = rows_updated + cursor.rowcount
    return rows_updated
        


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
    print "\t%s commands accepted from csv\n\t%s commands ignored from csv\n\t%s db records updated/added" %(accept_count,ignore_count,dbupdates)
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
group.add_argument('-v', '--vendor', type=str, help='upload vendor rates')
group.add_argument('-r', '--rates', type=str, help='generate rates')
group.add_argument('-a', '--add', type=str,choices=['vendor','product'], help='add product or vendors')
parser.add_argument('-f', '--file', type=str, help='file to process only usefull with -c destinations/vendors')
args = parser.parse_args()



############################ Main Code Here #######################################

if args.destination:
    upload_destinations(args.file)
elif args.vendor:
    upload_vendor_rates(args.file,args.vendor)
elif args.add:
    if args.add == 'vendor':
        add_vendor()
    elif args.add == 'product':
        add_product()

#fin.
