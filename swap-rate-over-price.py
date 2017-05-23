#!/usr/bin/env python3

# Blah
import argparse
import os.path
import logging
import pandas as pd
from pprint import pprint
import sys
import requests
import os

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



# Args  
parser = argparse.ArgumentParser()
parser.add_argument('--type', choices=[ 'btc','usd'], type=str, help='chart either btc or usd rates', required=True)
parser.add_argument('--historical', action='store_true', help='get historical data?')
args = parser.parse_args()




# API URL request
url = 'https://api.bitfinex.com/v2/candles/trade:1D:tBTCUSD/hist?limit=200'
request = json.loads(requests.get(url).text)

if args.historical == True:
	
	url = 'https://api.bitfinex.com/v2/candles/trade:1D:tBTCUSD/hist?limit=200&end='+str(request[len(request)-1][0])
	request2 = json.loads(requests.get(url).text)
	
	url = 'https://api.bitfinex.com/v2/candles/trade:1D:tBTCUSD/hist?limit=200&end='+str(request2[len(request2)-1][0])
	request3 = json.loads(requests.get(url).text)
	
	url = 'https://api.bitfinex.com/v2/candles/trade:1D:tBTCUSD/hist?limit=200&end='+str(request3[len(request3)-1][0])
	request4 = json.loads(requests.get(url).text)
	
	url = 'https://api.bitfinex.com/v2/candles/trade:1D:tBTCUSD/hist?limit=200&end='+str(request4[len(request4)-1][0])
	request5 = json.loads(requests.get(url).text)
	
	url = 'https://api.bitfinex.com/v2/candles/trade:1D:tBTCUSD/hist?limit=200&end='+str(request5[len(request5)-1][0])
	request6 = json.loads(requests.get(url).text)
	
	url = 'https://api.bitfinex.com/v2/candles/trade:1D:tBTCUSD/hist?limit=200&end='+str(request6[len(request6)-1][0])
	request7 = json.loads(requests.get(url).text)

	data_set = request + request2 + request3 + request4 + request5 + request6 + request7

else:

	data_set = request


candles = pd.read_json(json.dumps(data_set))
candles.rename(columns={0:'date', 1:'open', 2:'close', 3:'high', 4:'low', 5:'volume'}, inplace=True)
candles['date'] = pd.to_datetime( candles['date'], unit='ms' )
candles.set_index(candles['date'], inplace=True)
candles.sort_index(inplace=True)






# BTC
if args.type == 'btc': 
	fname = "vwarHourlyBTC.csv"
	color = '#a56a0b'



# USD
if args.type == 'usd':
	fname = "vwarHourlyUSD.csv"
	color = '#85BB65'


# Download file
urllib.request.urlretrieve("https://www.bfxdata.com/csv/"+fname, fname)


df = pd.read_csv(fname, skipinitialspace=True)
del df['Timestamp']
df['Date'] = pd.to_datetime( df['Date'] )
df.set_index(df['Date'], inplace=True)
df.sort_index(inplace=True)
df.columns = ['date','rate','opened']
df = df.resample('1D', closed='left', label='left').agg({'rate': 'mean', 'opened': 'sum' })
df = df.ix[candles.index[0]:]



if args.historical == True:
	plot_title_addon = " Historical "
	df['ema']  = df['rate'].ewm(span=8,min_periods=8,adjust=False).mean()
	df_plot    = df['ema'].values

	candles['ema'] = candles['close'].ewm(span=8,min_periods=8,adjust=False).mean()
	candles_plot   = candles['ema'].values

else:
	plot_title_addon = ""
	df_plot      = df['rate'].values
	candles_plot = candles['close'].values


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

ax1.set_title(plot_title_addon+'Bitcoin Price / Bitfinex '+args.type.upper()+' Daily VWap Rates')
ax1.xaxis_date()


ax1.plot( df.index.values, df_plot, color=color) 
ax1.set_ylabel(args.type.upper()+' Rates', color=color)
ax1.set_xscale("log", nonposx='clip')

ax2t.plot( candles['date'].values, candles_plot, color="b")
ax2t.set_ylabel('Bitcoin Price', color='#8c8a88')

im = Image.open('media/wp_logo.jpg')
# (fig.bbox.ymax - im.size[1])-20
fig.figimage(im, (fig.bbox.ymax / 2)+125, (fig.bbox.ymax - im.size[1])-10)

plt.savefig("btc_over_"+args.type+"_rates.png")
pprint('saved')

os.remove(fname)

sys.exit()