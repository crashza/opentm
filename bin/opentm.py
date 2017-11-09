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

def generate_rates(product):
    cnx          = connect_db()
    cursor       = cnx.cursor()
    pbar         = progressbar.ProgressBar()

    query        = 'SELECT i_product FROM products where name =\'%s\'' % product
    cursor.execute(query)
    for row in cursor:
        i_product = row[0]
    if  cursor.rowcount != 1:
        print 'unkown product : %s' % product
        exit()
    query       = 'SELECT * from product_defs where i_product = \'%s\'' % i_product
    cursor.execute(query)
    csv_array = []
    with open(args.output, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in cursor:
            new_array = get_rates_as_array(row)
            csv_array = csv_array + new_array
        writer.writerows(csv_array)

def get_rates_as_array(rows):
    i_product,i_group,value,charge_type,i_vendor = rows
    rates_array = []
    cnx         = connect_db()
    cursor      = cnx.cursor()

    query = ''' SELECT d.prefix,g.name,v.price
                FROM destinations d
                INNER JOIN groups g
                    ON d.i_group = g.i_group
                INNER JOIN vendor_rates v
                    ON d.i_destination = v.i_destination
                WHERE v.i_vendor = '%s' and d.i_group = %s
            '''
    cursor.execute(query %(i_vendor,i_group))
    for row in cursor:
        prefix,group,cost = row
        rate = calculate_rate(charge_type,value,cost)
        rates_array.append([prefix,group,cost,rate])
    return rates_array

def calculate_rate(charge_type,value,cost):
    calculated_rate = 0
    if charge_type == 1:
        calculated_rate = value
    elif charge_type == 2:
        calculated_rate = float(value) + float(cost)
    elif charge_type == 3:
        calculated_rate = float(cost) * (float(1) + float(value))
    elif charge_type == 4:
        calculated_rate = 100
    return calculated_rate


def add_vendor():
    vendor      = raw_input("enter vendor name :")
    description = raw_input("enter vednor desription :")
    cnx         = connect_db()
    cursor      = cnx.cursor()
    query       = 'INSERT into vendors (name,description) VALUES(\'%s\',\'%s\')' % (vendor,description)
    cursor.execute(query)
    cnx.commit()
    print "done"

def add_product():
    # TODO Lots of error checking here
    charge_types = {}
    groups       = {}
    cnx          = connect_db()
    cursor       = cnx.cursor()

    query        = 'SELECT i_group, name from groups'
    cursor.execute(query)
    for row in cursor:
        groups[row[0]] = row[1]
    
    product     = raw_input("enter product name :")
    description = raw_input("enter product desription :")
    query       = 'INSERT into products (name,description) VALUES(\'%s\',\'%s\')' % (product,description)
    cursor.execute(query)
    cnx.commit()
    for group in groups:
        ct  = raw_input("choose a charge type for %s :" %groups[group])
        val = raw_input("choose a value for %s :" %groups[group])
        ven = raw_input("choose a vendor for %s :" %groups[group])
        query = '''INSERT INTO product_defs 
                   (i_product,i_group,value,charge_type,i_vendor) 
                   SELECT p.i_product,g.i_group,'%s',c.i_charge_type,v.i_vendor 
                   from products p, groups g, vendors v, charge_types c
                   where p.name = '%s' and g.name = '%s'
                   and v.name = '%s' and c.name = '%s'
                '''
        cursor.execute(query % (val, product,groups[group], ven, ct))
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
    print "\t%s commands accepted from csv" % accept_count
    print "\t%s commands ignored from csv" % ignore_count
    print "\t%s db records updated/added" % dbupdates


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
    print "\t%s commands accepted from csv" % accept_count
    print "\t%s commands ignored from csv" % ignore_count
    print "\t%s db records updated/added" % dbupdates

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
parser.add_argument('-f', '--file', type=str, help='file to process only usefull with -d -v')
parser.add_argument('-o', '--output', type=str, help='output file only usefell with -r')
args = parser.parse_args()



############################ Main Code Here #######################################

if args.destination:
    upload_destinations(args.file)
elif args.vendor:
    upload_vendor_rates(args.file,args.vendor)
elif args.rates:
    generate_rates(args.rates)
elif args.add:
    if args.add == 'vendor':
        add_vendor()
    elif args.add == 'product':
        add_product()

#fin.
