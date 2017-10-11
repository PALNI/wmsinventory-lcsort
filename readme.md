# OCLC WMS Inventory File Call Number Sorting

This script is designed to perform the following functions:

* Fetch the weekly inventory file from an institution's WMS reporting FTP directory
* Normalize and sort all inventory items by LC call number (Dewey numbers will not be normalized/modified)
* Output the sorted inventory to a new FTP directory, publish to a web page, and email the sorted inventory to a list of users

The following fields are included in the output file:
* Call Number (will output as its non-normalized form)
* Title
* Author
* Barcode
* Location
* Status
* Inventory Date

The script presumes installation on a server with Python 2.x and above and requires installation of the Python call number library:

https://github.com/libraryhackers/library-callnumber-lc/tree/master/python

It can be scheduled to run automatically weekly each Monday via crontab, e.g.:

5 1 * * 1 /location/of/ftp.py

replace 'location/of' with the location you've installed this repository, e.g., /var/local/wmsinventory-lcsort

## Setup

Copy config.py.sample to config.py and fill in all values.

The script is designed to be run on a Monday and fetch the preceding day's (Sunday's) inventory file.  

During testing, enter in a filename date in the testfile value in config.py to hardcode it, so that you can run the script anytime and the same file will be fetched each time.

After testing when ready to move to production, be sure to modify ftp.py to comment out each of the testing lines and uncomment the associated production line.

Search for #testing and #production in the file - there are three sections that need to be changed.
