FTP and Shelflist script for OCLC WMS Inventory Reports
=======================================================

This script is designed to run as a scheduled cron job, where the cron runs on a Monday morning (e.g., 12:01 AM Monday).

It automatically FTP's yesterday's (Sunday's) inventory report for WMS.  It then normalizes Library of Congress call numbers and sorts them.

To use:  copy config.py.sample to config.py and fill in credentials for accessing the WMS FTP reports server.    

This script is indebted to Michael J. Giarlo's excellent LC Call Number normalization library [library-callnumber-lc](https://github.com/libraryhackers/library-callnumber-lc/tree/master/python "Library of Congress Normalization Library").  Thanks also to Richard Lammert of Concordia Theological Seminary of Fort Wayne for sharing the perl script upon which this is based.


