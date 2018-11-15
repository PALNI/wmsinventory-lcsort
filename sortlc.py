#!/usr/bin/env python

#To run: name CSV file 'input.csv' and place in same directory as this file
#The CSV file must have a header row and be encoded in UTF-8
#In Terminal / Bash, run python sortlc.py or python3 sortlc.py
#An output file will be created with a new column containing sortable call numbers
#Instructions for installing pycallnumber: https://github.com/unt-libraries/pycallnumber

import csv
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
    sortedlist = sorted(all, key=operator.itemgetter(0))
    writer.writerows(sortedlist)
     