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
import zipfile
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.mime.text import MIMEText
from email import Encoders

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

#PRODUCTION - uncomment line below in production
filematch = config.symbol + '.Item_Inventories.' + yesterday + '.txt'

#TESTING - uncomment line below when testing
#filematch = config.symbol + config.testfile

#Retrieve the files
for filename in ftp.nlst(filematch):
  fhandle = open(filename, 'wb')
  print 'Getting ' + filename
  ftp.retrbinary('RETR ' + filename, fhandle.write)
  fhandle.close()
#Close the FTP Connection
ftp.quit()

#Open the most recent file
#PRODUCTION - uncomment line below in production
mostrecent = open(config.symbol + '.Item_Inventories.' + str(yesterday) + '.txt', 'r')
#TESTING - uncomment line below when testing
#mostrecent = open(config.symbol + config.testfile, 'r')

#read the inventory file  
csv1 = csv.reader(mostrecent, delimiter='|', quoting=csv.QUOTE_NONE)

#write normalized call numbers to a temp file
csv_out = csv.writer(open('temp.txt', 'w'), delimiter = '\t', quotechar = '"', quoting = csv.QUOTE_MINIMAL)

#define row elements and ignore withdrawn
for row in csv1:
  call = location = temploc = author = barcode = status = description = invdate = ''
  call = row[5]
  location = row[2]
  temploc = row[3]
  title = row[7]
  author = row[6]
  barcode = row[12]
  status = row[16]
  description = row[8]
  invdate = row[20]
  if temploc != '---':
    location = temploc
  if description != '---':
    call = call + ' ' + description
    call2 = call + ' ' + description   
  if status != 'WITHDRAWN':
    lcmatch = re.compile('[A-Z]{1,3}\d')
    deweymatch = re.compile('\d*\.\d*')
    if lcmatch.match(call):
      call2 = call.replace('-','v')  
      sortcall = callnumber.normalize(call2)
      if sortcall == None:
        csv_out.writerow([call,call,title,author,barcode,location,status,invdate])
      else:
        if sortcall.find('PT') != -1:
          partsplit = sortcall.split('PT')
          partsplitnum = partsplit[1].rjust(3, '0')
          sortcall = partsplit[0] + 'PT' + partsplitnum
        if call.find('v.') != -1:
          #if v. and no normalized V
           if sortcall.find('V') == -1:
             sortedsplit = call.split('v.')
             vcallsortnum = sortedsplit[1].rjust(3, '0')
             sortcall = sortcall + ' V' + vcallsortnum
             #csv_out.writerow([sortcall,call,title,author,barcode,location]) 
           #else if v. and normalized V 
           elif sortcall.find('V') != -1:
             sortedsplit = sortcall.split('V')
             vcallsortnum = sortedsplit[1].rjust(3, '0')
             if len(sortedsplit) > 2:
               vcallsortnum2 = sortedsplit[2].rjust(3,'0')
               sortcall = sortedsplit[0] + 'V' + vcallsortnum + 'V' + vcallsortnum2
               #csv_out.writerow([sortcall,call,title,author,barcode,location])
             else:
               sortcall = sortedsplit[0] + 'V' + vcallsortnum
               #csv_out.writerow([sortcall,call,title,author,barcode,location])
           #else:
             #csv_out.writerow([sortcall,call,title,author,barcode,location])
        csv_out.writerow([sortcall,call,title,author,barcode,location,status,invdate])
    elif deweymatch.match(call):
      csv_out.writerow([call,call,title,author,barcode,location,status,invdate])
    else:
      accession = re.split('(\d+)', call)
      if len(accession) > 3:
        padded = accession[1].rjust(5,'0')
        padded2 = accession[3].rjust(5,'0')
        csv_out.writerow([accession[0] + padded + accession[2] + padded2,call,title,author,barcode,location,status,invdate])
      elif len(accession) > 2:
        padded = accession[1].rjust(5, '0') 
        csv_out.writerow([accession[0] + padded,call,title,author,barcode,location,status,invdate])
      else:
        csv_out.writerow([call,call,title,author,barcode,location,status,invdate])

#read temp file and write to sorted file    
csv2_out = csv.writer(open('sorted' + str(yesterday) + '.txt', 'wb'), delimiter = '\t', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
csv2_out.writerow(['Call Number', 'Title', 'Author','Barcode','Location','Status','InventoryDate'])
data = csv.reader(open('temp.txt'),delimiter='\t',quoting=csv.QUOTE_NONE)

sortedlist = sorted(data, key=operator.itemgetter(0))

for row in sortedlist:

  sortednormal = sortedcall = sortedtitle = sortedauthor = sortedbarcode = sortedlocation = sortedstatus = sortedinvdate = ''
  if len(row) > 5:
    try:
      sortednormal = row[0]
    except IndexError:
      sortednormal = ''

    try:
      sortedcall = row[1]
    except IndexError:
      sortedcall = ''
    
    try:
      sortedtitle = row[2]
    except IndexError:
      sortedtitle = ''

    try:
      sortedauthor = row[3]
    except IndexError:
      sortedauthor = ''

    try:
      sortedbarcode = row[4]
    except IndexError:
      sortedbarcode = ''

    try:
      sortedlocation = row[5]
    except IndexError:
      sortedlocation = '' 

    try:
      sortedstatus = row[6]
    except IndexError:
      sortedstatus = ''

    try:
      sortedinvdate = row[7]
    except IndexError:
      sortedinvdate = ''
  
  csv2_out.writerow([sortedcall,sortedtitle,sortedauthor,sortedbarcode,sortedlocation,sortedstatus,sortedinvdate])

# Remove the temp file
os.remove('temp.txt')

#copy files to a web directory
shutil.copy2(filematch, config.destination)
shutil.copy2('sorted' + str(yesterday) + '.txt', config.destination)

#Zip the file
zf = zipfile.ZipFile('sorted.zip', "w", zipfile.ZIP_DEFLATED)
zf.write('sorted' + str(yesterday) + '.txt')
zf.close()

#email the sorted file to library contact
msg = MIMEMultipart()
msg['Subject'] = config.SUBJECT
msg['From'] = config.EMAIL_FROM
msg['To'] = config.EMAIL_TO

part = MIMEBase('application', 'zip')
zf = open('sorted.zip', 'rb')
part.set_payload(zf.read())
#part.set_payload(open('sorted' + str(yesterday) + '.txt', "rb").read())
Encoders.encode_base64(part)

part.add_header('Content-Disposition', 'attachment; filename="sorted.zip"')

msg.attach(part)

server = smtplib.SMTP(config.EMAIL_SERVER)
server.ehlo()
server.starttls()
server.login(config.EMAIL_FROM, config.SMTP_PASS)
server.sendmail(config.EMAIL_FROM, config.EMAIL_RECIP, msg.as_string())
server.quit()

#delete the sorted file from this directory
os.remove('sorted' + str(yesterday) + '.txt')

#PRODUCTION - uncomment line below in production
os.remove(config.symbol + '.Item_Inventories.' + str(yesterday) + '.txt')

#TESTING - uncomment line below when testing)
#os.remove(config.symbol + config.testfile)
