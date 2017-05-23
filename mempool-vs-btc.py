#!/usr/bin/env python3

# Blah
from argparse import ArgumentParser
import os.path
import logging
import pandas as pd
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




url = "https://api.blockchain.info/charts/mempool-size?format=json&timespan=all"
decodeddata = json.loads(requests.get(url).text)

mempool = pd.DataFrame(columns=('date','bytes'))

for data in decodeddata['values']:
    mempool.loc[data['x']] = [data['x'], data['y']]

# Set the index 
mempool['date'] = pd.to_datetime( mempool['date'], unit='s' )

# Set the index 
mempool.set_index(mempool['date'], inplace=True)
del mempool['date']
# Sort it
mempool.sort_index(inplace=True)

mempool = mempool.resample('1D', closed='left', label='left').agg({'bytes': 'mean' })
mempool = mempool.ix[candles.index[0]:]



#pprint(len(decodeddata))
#pprint(decodeddata)
# pprint(decodeddata)
pprint(candles.head())
pprint(mempool.head())





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

ax1.set_title('Bitcoin Price / Mempool Size - Whalepool.io')
ax1.xaxis_date()

mempool['bytes_ema'] = mempool['bytes'].ewm(span=8,min_periods=8,adjust=False).mean()

ax1.plot( mempool.index.values, mempool['bytes_ema'].values, color='b') 
ax1.set_ylabel('bytes', color='b')

ax2t.plot( candles['date'].values, candles['close'].values, color="g")
ax2t.set_ylabel('bitcoin price', color='g')

im = Image.open('media/wp_logo.jpg')
# (fig.bbox.ymax - im.size[1])-20
fig.figimage(im, (fig.bbox.ymax / 2)+125, (fig.bbox.ymax - im.size[1])-10)

plt.savefig("mempool-over-btc.png")
pprint('saved')


sys.exit()