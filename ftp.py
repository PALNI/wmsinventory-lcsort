#!/usr/bin/env python
import os
import ftplib
import sys
import callnumber
import csv
import re
import operator
import shutil
import datetime
from datetime import timedelta

#get configuration file with FTP credentials
import config

#Open ftp connection
ftp = ftplib.FTP(config.domain, config.username, config.password)

#navigate to the reports directory
ftp.cwd("/wms/reports")
#Define yesterday
yesterday = datetime.date.today() - timedelta(days=1)
#date = datetime.date.today()
yesterday = yesterday.strftime('%Y%m%d')

#For production, uncomment line below to get yesterday's file
filematch = config.symbol + '.Item_Inventories.' + yesterday + '.txt'

#For testing, uncomment line below to get specific file
#filematch = config.symbol + '.Item_Inventories.20150726.txt'

#Retrieve the files
for filename in ftp.nlst(filematch):
  fhandle = open(filename, 'wb')
  print 'Getting ' + filename
  ftp.retrbinary('RETR ' + filename, fhandle.write)
  fhandle.close()
#Close the FTP Connection
ftp.quit()

#Open the most recent file
#for production uncomment line below
mostrecent = open(config.symbol + '.Item_Inventories.' + str(yesterday) + '.txt', 'r')
#for testing uncomment line below
#mostrecent = open(config.symbol + '.Item_Inventories.20150726.txt', 'r')

#read the inventory file  
csv1 = csv.reader(mostrecent, delimiter='|', quoting=csv.QUOTE_NONE)

#write normalized call numbers to a temp file
csv_out = csv.writer(open('temp.txt', 'w'), delimiter = '\t', quotechar = '"', quoting = csv.QUOTE_MINIMAL)

#define row elements and ignore withdrawn
for row in csv1:
  call = row[5]
  location = row[2]
  temploc = row[3]
  title = row[7]
  author = row[6]
  barcode = row[12]
  status = row[16]
  description = row[8]
  if temploc != '---':
    location = temploc
  if description != '---':
    call = call + ' ' + description
  #if description.find('v')!= -1:
    #volno = description.split('v.')
    #if volno[1] is not None:
      #volsort = volno[1].rjust(3, '0') 
      #volume = 'V' + volsort
    #else: 
      #volume = 'novfound'
  #else:
    #volume = 'no find' + description   
  if status != 'WITHDRAWN':
    lcmatch = re.compile('[A-Z]{1,3}\d')
    if lcmatch.match(call):
      sortcall = callnumber.normalize(call)
      if sortcall == None:
        csv_out.writerow([call,call,title,author,barcode,location])
      elif call.find('v.') != -1:
        if sortcall.find('V') == -1:
         sortedsplit = call.split('v.')
         vcallsortnum = sortedsplit[1].rjust(3, '0')
         sortcall = sortcall + ' V' + vcallsortnum
        elif sortcall.find('V') != -1:
          sortedsplit = sortcall.split('V')
          vcallsortnum = sortedsplit[1].rjust(3, '0')
          sortcall = sortedsplit[0] + 'V' + vcallsortnum
        csv_out.writerow([sortcall,call,title,author,barcode,location])
      else:
       csv_out.writerow([sortcall,call,title,author,barcode,location])
    else:
      csv_out.writerow([call,call,title,author,barcode,location])

#read temp file and write to sorted file    
csv2_out = csv.writer(open('sorted' + str(yesterday) + '.txt', 'wb'), delimiter = '\t', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
csv2_out.writerow(['Call Number', 'Title', 'Author','Barcode','Location'])
data = csv.reader(open('temp.txt'),delimiter='\t')

sortedlist = sorted(data, key=operator.itemgetter(0))

for row in sortedlist:

  sortednormal = sortedcall = sortedtitle = sortedauthor = sortedbarcode = sortedlocation = ''
  if len(row) > 5:
    if row[0] is not None:
      sortednormal = row[0]

    if row[1] is not None:
      sortedcall = row[1]

    if row[2] is not None:
      sortedtitle = row[2]

    if row[3] is not None:
      sortedauthor = row[3]
    else:
      sortedauthor = ''

    if row[4] is not None:
      sortedbarcode = row[4]
    else:
      sortedbarcode = ''

    if row[5] is not None:
      sortedlocation = row[5]
    else:
      sortedlocation = '' 
  
  elif len(row) > 4:
    if row[0] is not None:
      sortednormal = row[0]
  
    if row[1] is not None:
      sortedcall = row[1]
  
    if row[2] is not None:
      sortedtitle = row[2]
 
    if row[3] is not None:
      sortedauthor = row[3]
    else: 
      sortedauthor = ''

    if row[4] is not None:
      sortedbarcode = row[4]
    else: 
      sortedbarcode = ''
 
  elif len(row) < 2:
    if row[0] is not None:
      sortednormal = row[0]

  elif len(row) < 3:
    if row[0] is not None:
      sortednormal = row[0]
    
    if row[1] is not None:
      sortedcall = row[1]

  elif len(row) < 4:
    if row[0] is not None:
      sortednormal = row[0]

    if row[1] is not None:
      sortedcall = row[1]

    if row[2] is not None:
      sortedtitle = row[2]

  csv2_out.writerow([sortedcall,sortedtitle,sortedauthor,sortedbarcode,sortedlocation])

# Remove the temp file
os.remove('temp.txt')

#copy files to a web directory
shutil.copy2(filematch, config.destination)
shutil.copy2('sorted' + str(yesterday) + '.txt', config.destination)
