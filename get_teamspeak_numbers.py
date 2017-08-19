#!/usr/bin/env python3
# import argparse, urllib, ast, datetime, pprint, re, csv
# import pandas as pd
# import sys
# import json
# Custom
import utils
import os

import datetime
import ts3 
from pprint import pprint
from pymongo import MongoClient



client = MongoClient('mongodb://localhost:27017')
db = client.whalepool
timestamp = datetime.datetime.utcnow()

"""
Get Teamspeak User count
"""
ts_user_count = None 
with ts3.query.TS3Connection(os.environ.get('TS_IP'), 2009) as ts3conn:
	try:
		ts3conn.login(
		client_login_name=os.environ.get('TS_USERNAME'),
		client_login_password=os.environ.get('TS_PASSWORD')
		)
	except ts3.query.TS3QueryError as err:
		print("Login failed:", err.resp.error["msg"])
		exit(1)
	ts3conn.use(sid=778)
	resp = ts3conn.clientlist()
	ts_user_count = len(resp.parsed)-1

	info = { 'timestamp': timestamp, 'users': ts_user_count }
	db.teamspeak_numbers.insert( info )

	pprint(timestamp)
	pprint(ts_user_count)

	ts3conn.quit()

