#!/usr/bin/env python
import os
import ftplib
import sys
#import callnumber
import csv
import re
import operator
import shutil
import datetime
from datetime import timedelta
import zipfile
import smtplib
import pycallnumber as pycn

with open('input.csv',encoding='utf-8', errors='ignore') as infile:  # Use 'with' to close files automatically
  reader = csv.reader(infile)
  
  with open('output.csv', 'w') as outfile:
    
    writer = csv.writer(outfile, delimiter=',', lineterminator='\n')
    all = []
    row = next(reader)
    row.append('Call Number')
    all.append(row)
    for row in reader:  # Read remaining data from our input CSV
      callnumber = pycn.callnumber(row[0]) 
      sortcall = callnumber.for_sort()
      row[0] = sortcall
      row.append(callnumber)
      all.append(row)
      
      #writer.writerow(all)
      
    
    sortedlist = sorted(all, key=operator.itemgetter(0))
    writer.writerows(sortedlist)
     