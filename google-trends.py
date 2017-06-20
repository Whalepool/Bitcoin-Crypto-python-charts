#!/usr/bin/env python3

# Blah
import argparse 
import os
import os.path
import logging
import pandas as pd
import numpy as np 
from pprint import pprint
import sys
import requests
import datetime

# API 
import hmac
import time
import hashlib
from future.builtins import bytes 
import urllib.request
import json

# Charting
import talib as ta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from PIL import Image

# google Trends
from pytrends.request import TrendReq


# Configure Logging
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')
logger.info('Beginning...')


# Args  
parser = argparse.ArgumentParser()
parser.add_argument('--historical', action='store_true', help='get historical data?')
args = parser.parse_args()


envars = ['GUSERNAME','GPASS']
errors = 0 
for v in envars:
	if os.environ.get(v) is not None:
		logger.info('Found env var: '+v)
		pass
	else:
		errors += 1 
		pprint('Please set a '+v+' envionment variable.')

if errors > 0:
	sys.exit()


#####################
# Make Trends Request
#####################
trend_tf = "now 7-d"
candle_tf = "1H"
if args.historical == True:
	trend_tf = "today 3-m"
	candle_tf = '1D'

logger.info('Setting google trend object')
pytrend = TrendReq(os.environ.get('GUSERNAME'), os.environ.get('GPASS'), custom_useragent='Whalepool Trend Checker')

logger.info('Building google trend payload')
pytrend.build_payload(kw_list=['bitcoin'],timeframe=trend_tf)

logger.info('Making interest over time dataframe')
trends = pytrend.interest_over_time()


# Get the earliest record
epoch = datetime.datetime.utcfromtimestamp(0)
trend_start_ms = (trends.index[0] - epoch).total_seconds() * 1000.0
logger.info('Earliest dated record from trends: '+str(trends.index[0]))


######################
# Make Candles Request
######################
url = 'https://api.bitfinex.com/v2/candles/trade:'+candle_tf+':tBTCUSD/hist?limit=200&start='+str(trend_start_ms)
request = json.loads(requests.get(url).text)
data_set = request

# Build candles dataframe
candles = pd.read_json(json.dumps(data_set))
candles.rename(columns={0:'date', 1:'open', 2:'close', 3:'high', 4:'low', 5:'volume'}, inplace=True)
candles['date'] = pd.to_datetime( candles['date'], unit='ms' )
candles.set_index(candles['date'], inplace=True)
candles.sort_index(inplace=True)


######################
# Output some data
######################
logger.info('Trends: ')
pprint(trends.head())
pprint(trends.tail())
logger.info('Candles: ')
pprint(candles.head())
pprint(candles.tail())


#######################
# Make the plot... 
#######################

# Enable a Grid
plt.rc('axes', grid=True)
# Set Grid preferences 
plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

# Create a figure, 16 inches by 12 inches
fig = plt.figure(facecolor='white', figsize=(11, 7), dpi=100)

# Draw 3 rectangles
# left, bottom, width, height
left, width = 0.1, 0.8
rect1 = [left, 0.1, width, 0.8]
# rect2 = [left, 0.27, width, 0.17]

ax1 = fig.add_axes(rect1, facecolor='#f6f6f6')  
ax1.set_xlabel('date')
# ax2 = fig.add_axes(rect2, facecolor='#f6f6f6', sharex=ax1)
ax2t = ax1.twinx()

ax1.set_title('Bitcoin Price / Google Trends - Whalepool.io')
ax1.xaxis_date()

ax1.plot( trends.index.values, trends['bitcoin'].values, color='b') 
ax1.set_ylabel('trends', color='b')

ax2t.plot( candles['date'].values, candles['close'].values, color="g", linewidth=2)
ax2t.set_ylabel('bitcoin price', color='g')

im = Image.open('media/wp_logo.jpg')
# (fig.bbox.ymax - im.size[1])-20
fig.figimage(im, (fig.bbox.ymax / 2)+125, (fig.bbox.ymax - im.size[1])-10)

plt.savefig("google-trends-vs-btc.png")
pprint('saved')


sys.exit()