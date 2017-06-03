#!/usr/bin/env python3

# Blah
from argparse import ArgumentParser
import os.path
import logging
import pandas as pd
import numpy as np 
from pprint import pprint
import sys
import requests

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



# Configure Logging
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')





# API URL request
url = 'https://api.bitfinex.com/v2/candles/trade:1D:tBTCUSD/hist?limit=200&start=1476831600000'
request = json.loads(requests.get(url).text)

url = 'https://api.bitfinex.com/v2/candles/trade:1D:tBTCUSD/hist?limit=200&end='+str(request[len(request)-1][0])
request2 = json.loads(requests.get(url).text)

url = 'https://api.bitfinex.com/v2/candles/trade:1D:tBTCUSD/hist?limit=200&end='+str(request2[len(request2)-1][0])
request3 = json.loads(requests.get(url).text)


data_set = request + request2 + request3 

candles = pd.read_json(json.dumps(data_set))
candles.rename(columns={0:'date', 1:'open', 2:'close', 3:'high', 4:'low', 5:'volume'}, inplace=True)
candles['date'] = pd.to_datetime( candles['date'], unit='ms' )
candles.set_index(candles['date'], inplace=True)
# Sort it
candles.sort_index(inplace=True)

pprint(candles.head())
pprint(candles.tail())




trends = pd.read_csv("google-trends.csv", skipinitialspace=True)
trends.columns = ['date','trend']
trends['date'] = pd.to_datetime( trends['date'], dayfirst=True, format="%d/%m/%Y" )
trends.set_index(trends['date'], inplace=True)
trends = trends.ix[candles.index[0]:]
# del trends['date']


pprint(trends.head())
pprint(trends.tail())





# Plot chart from csv
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


# ax1.plot( trends.index.values, trends['trend'].values, color='b') 
# ax1.plot( trends.index.values, trends['trend'].values, color='b') 

# As a percentile
# percentiles = trends['trend'].quantile(np.linspace(.1, 1, 9, 0))
# percentiles = trends['trend'].quantile(np.linspace(.05, 1, 10, 0))
# for alpha,value in percentiles.iteritems():
# 	alpha = round(float(alpha),1)
# 	msk = (trends['trend'] >= value)
# 	df = trends[msk]
# 	ax1.bar(df.index.values, df['trend'].values, width=2, alpha=alpha, color='#552B72')

masks = [
	[0, 10, 0.1],
	[10, 20, 0.2],
	[20, 30, 0.3],
	[30, 40, 0.4],
	[40, 50, 0.5],
	[50, 60, 0.6],
	[60, 70, 0.7],
	[70, 80, 0.8],
	[80, 90, 0.9],
	[80, 100, 1]
]
for m in masks: 
	msk = (trends['trend'] >= m[0]) & (trends['trend'] <= m[1])
	df = trends[msk]
	ax1.bar(df.index.values, df['trend'].values, width=2, alpha=m[2], color='#552B72')

	


ax1.set_ylabel('trends', color='b')

ax2t.plot( candles['date'].values, candles['close'].values, color="g", linewidth=2)
ax2t.set_ylabel('bitcoin price', color='g')

im = Image.open('media/wp_logo.jpg')
# (fig.bbox.ymax - im.size[1])-20
fig.figimage(im, (fig.bbox.ymax / 2)+125, (fig.bbox.ymax - im.size[1])-10)

plt.savefig("google-trends-vs-btc.png")
pprint('saved')


sys.exit()