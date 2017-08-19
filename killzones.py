#!/usr/bin/env python3

# Custom
import utils

# Blah
import logging
import pandas as pd
import numpy as np
from pprint import pprint
import sys
import os
import requests
import datetime 
import json
import time

# # Charting
import talib as ta
import matplotlib.pyplot as plt
from PIL import Image


# Configure Logging
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')



SCRIPT_DIR   = os.path.dirname(os.path.realpath(__file__))
FILENAME     = SCRIPT_DIR+"/killzones.png"
LOGO_PATH		 = SCRIPT_DIR+'/media/wp_logo.jpg'
SLEEP_TIMER = 2



##########################
# Get the candles
##########################

url = 'https://api.bitfinex.com/v2/candles/trade:30m:tBTCUSD/hist?limit=200'
candles_json = json.loads(requests.get(url).text)

while len(candles_json) < 399:
	time.sleep(SLEEP_TIMER)
	earliest = (candles_json[len(candles_json)-1])[0] - 1
	url = 'https://api.bitfinex.com/v2/candles/trade:30m:tBTCUSD/hist?limit=200&end=%s'
	query = url % earliest
	result = json.loads(requests.get(query).text)
	candles_json += result



candles = pd.read_json(json.dumps(candles_json))
candles.rename(columns={0:'date', 1:'open', 2:'close', 3:'high', 4:'low', 5:'volume'}, inplace=True)
candles['date'] = pd.to_datetime( candles['date'], unit='ms' )
candles.set_index(candles['date'], inplace=True)
candles.sort_index(inplace=True)
candles.index = candles.index + pd.DateOffset(hours=1)

del candles['date']



##########################
# Volatility functions
##########################
candles['open'].fillna(0, inplace=True)
candles['high'].fillna(0, inplace=True)
candles['low'].fillna(0, inplace=True)
candles['close'].fillna(0, inplace=True)

# Average True Range
atr = ta.ATR( candles['high'].values, candles['low'].values, candles['close'].values, timeperiod=14)
candles['atr'] = 0
candles['atr'] = atr
candles['atr'].fillna(0, inplace=True)

# Normalized Average True Range
natr = ta.NATR( candles['high'].values, candles['low'].values, candles['close'].values, timeperiod=14)
candles['natr'] = 0
candles['natr'] = natr
candles['natr'].fillna(0, inplace=True)

# True Range
tr = ta.TRANGE( candles['high'].values, candles['low'].values, candles['close'].values)
candles['tr'] = 0
candles['tr'] = tr
candles['tr'].fillna(0, inplace=True)




##########################
# Data for bar charts .. labels and data..
##########################

labels = []
values = []

labels.append('Asian Session')
mask = (candles.index.hour >= 0) & (candles.index.hour < 10) & (candles.index.weekday < 5)
values.append(candles[mask]['atr'].mean(skipna=True))

labels.append('Asian Range')
mask = (candles.index.hour >= 0) & (candles.index.hour < 5) & (candles.index.weekday < 5)
values.append(candles[mask]['atr'].mean(skipna=True))

# labels.append('Asian Kill Zone')
# mask = (candles.index.hour >= 23) & (candles.index.hour < 3) & (candles.index.weekday < 5)
# values.append(candles[mask]['atr'].mean(skipna=True))
# mask = (candles.index.hour+24 < 3)

labels.append('London Session')
mask = (candles.index.hour >= 8) & (candles.index.hour < 17) & (candles.index.weekday < 5)
values.append(candles[mask]['atr'].mean(skipna=True))

labels.append('London Open Kill Zone')
mask = (candles.index.hour >= 7) & (candles.index.hour < 9) & (candles.index.weekday < 5)
values.append(candles[mask]['atr'].mean(skipna=True))

labels.append('London Close Kill Zone')
mask = (candles.index.hour >= 16) & (candles.index.hour < 18) & (candles.index.weekday < 5)
values.append(candles[mask]['atr'].mean(skipna=True))

labels.append('New York Session')
mask = (candles.index.hour >= 13) & (candles.index.hour < 22) & (candles.index.weekday < 5)
values.append(candles[mask]['atr'].mean(skipna=True))

labels.append('New York Open Kill zone')
mask = (candles.index.hour >= 12) & (candles.index.hour < 14) & (candles.index.weekday < 5)
values.append(candles[mask]['atr'].mean(skipna=True))



h_lables = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
h_values = []
for i in h_lables:
	mask = (candles.index.hour == i)
	h_values.append(candles[mask]['atr'].mean(skipna=True))



###############################


#start = str(datetime.datetime.fromtimestamp(candles_json[len(candles_json)-1][0]/1000.0).strftime("%Y-%m-%d"))
#end = str(datetime.datetime.fromtimestamp(candles_json[0][0]/1000.0).strftime("%Y-%m-%d"))
start = datetime.datetime.fromtimestamp(candles_json[len(candles_json)-1][0]/1000.0)
end = datetime.datetime.fromtimestamp(candles_json[0][0]/1000.0)
delta = end - start



plt.rc('axes', grid=False)
fig = plt.figure(facecolor='white', figsize=(11, 13), dpi=100)
fig.suptitle('Bitcoin Volatility in the last '+str(delta.days)+' days', fontsize=14, fontweight='bold')

# left, bottom, width, height
rect_hourly = [0.1, 0.6, 0.8, 0.3]
rect_kilzone = [0.1, 0.18, 0.8, 0.3]


N = len(h_lables)
ind = np.arange(N)  
width = 0.35 


ax2 = fig.add_axes(rect_hourly, facecolor='#f6f6f6')  
ax2.bar(ind, h_values, width, color='b', bottom=0)
ax2.set_ylabel('ATR Value')
ax2.set_title('Hours of the day (GMT)', fontsize=14)
ax2.set_xticks(ind)
ax2.set_xticklabels(h_lables, rotation=90, fontsize=11,stretch='ultra-condensed')


###############################


N = len(labels)
ind = np.arange(N) 
width = 0.35 

ax1 = fig.add_axes(rect_kilzone, facecolor='#f6f6f6')  
ax1.bar(ind, values, width, color='b', bottom=0) 
ax1.set_ylabel('ATR Value')
ax1.set_title('Killzones', fontsize=14)
ax1.set_xticks(ind)
ax1.set_xticklabels(labels, rotation=90, fontsize=11,stretch='ultra-condensed')


###############################


im = Image.open(LOGO_PATH)
fig.figimage(im, 50, (fig.bbox.ymax - im.size[1])-10)


plt.savefig(FILENAME)


n = utils.Notify()
n.telegram({
		'chat_id': '@whalepoolbtcfeed',
		'message': 'Recent bitcoin volatility periods',
		'picture': FILENAME
	})
print('Saved: '+FILENAME)
os.remove(FILENAME)
sys.exit()




