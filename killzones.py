#!/usr/bin/env python3

# Blah
import argparse
import os.path
import logging
import pandas as pd
import numpy as np
from pprint import pprint
import sys
import requests
import os
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


# Configure Logging
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')

# Times in GMT
killzones = [
	{ 
		'name': 'Asian Session', 
		'start': 0, 
		'end': 10 
	},
	{ 
		
		'name': 'Asian Range', 
		'start': 0, 
		'end': 5 
	},
	{ 	
		'name': 'Asian Kill Zone', 
		'start': 23, 
		'end': 3
		# 'end_day_delta': 1
	},
	{ 	
		'name': 'London Session', 
		'start': 8, 
		'end': 17 
	},
	{ 	
		'name': 'London Open Kill Zone', 
		'start': 7, 
		'end': 9 
	},
	{ 	
		'name': 'London Close Kill Zone', 
		'start': 16, 
		'end': 18 
	},
	{ 	
		'name': 'New York Session', 
		'start': 13, 
		'end': 22 
	},
	{ 	
		'name': 'New York Open Kill Zone', 
		'start': 12, 
		'end': 14 
	}
]

# Create a key 
for index, k in enumerate(killzones):
	killzones[index]['key'] = k['name'].replace(' ','_').lower()




##########################
# Get the candles
##########################
sleep_timer = 2

url = 'https://api.bitfinex.com/v2/candles/trade:30m:tBTCUSD/hist?limit=200'
request = json.loads(requests.get(url).text)
time.sleep(sleep_timer)
url = 'https://api.bitfinex.com/v2/candles/trade:30m:tBTCUSD/hist?limit=200&end='+str(request[len(request)-1][0])
request2 = json.loads(requests.get(url).text)
time.sleep(sleep_timer)
url = 'https://api.bitfinex.com/v2/candles/trade:30m:tBTCUSD/hist?limit=200&end='+str(request2[len(request2)-1][0])
request3 = json.loads(requests.get(url).text)
# time.sleep(sleep_timer)
# url = 'https://api.bitfinex.com/v2/candles/trade:30m:tBTCUSD/hist?limit=200&end='+str(request3[len(request3)-1][0])
# request4 = json.loads(requests.get(url).text)
# time.sleep(sleep_timer)
# url = 'https://api.bitfinex.com/v2/candles/trade:30m:tBTCUSD/hist?limit=200&end='+str(request4[len(request4)-1][0])
# request5 = json.loads(requests.get(url).text)
# time.sleep(sleep_timer)
# url = 'https://api.bitfinex.com/v2/candles/trade:30m:tBTCUSD/hist?limit=200&end='+str(request5[len(request5)-1][0])
# request6 = json.loads(requests.get(url).text)
# time.sleep(sleep_timer)
# url = 'https://api.bitfinex.com/v2/candles/trade:30m:tBTCUSD/hist?limit=200&end='+str(request6[len(request6)-1][0])
# request7 = json.loads(requests.get(url).text)
# time.sleep(sleep_timer)

# candles_json = request + request2 + request3 + request4 + request5 + request6 + request7
candles_json = request + request2 + request3
# candles_json = request 


# text_file = open("candles.json", "w")
# text_file.write(json.dumps(candles_json))
# text_file.close()


# To work from strored file
# with open('candles.json') as json_data:
#  	candles_json = json.load(json_data)





##########################
# Create a data frame 
##########################


candles = pd.read_json(json.dumps(candles_json))
candles.rename(columns={0:'date', 1:'open', 2:'close', 3:'high', 4:'low', 5:'volume'}, inplace=True)
candles['date'] = pd.to_datetime( candles['date'], unit='ms' )
candles.set_index(candles['date'], inplace=True)
candles.sort_index(inplace=True)
# candles.index = candles.index + pd.DateOffset(hours=1)

del candles['date']

for k in killzones:
	candles[k['key']] = False




start = datetime.datetime.fromtimestamp(candles_json[len(candles_json)-1][0]/1000.0)
end = datetime.datetime.fromtimestamp(candles_json[0][0]/1000.0)



##########################
# Go through candles look to see if they're in killzones etc or not 
##########################

for row in reversed(candles_json):
	# 0 = Millisecond time
	# 1 = Open 
	# 2 = Close 
	# 3 = High 
	# 4 = Low 
	# 5 = Volume 

	currtime = datetime.datetime.fromtimestamp(row[0]/1000.0)
	currtime = currtime + datetime.timedelta(hours=-1)

	for k in killzones: 
		# if k['name'] == 'Asian Kill Zone':

		start = currtime.replace(hour=k['start'],minute=0)

		if currtime.hour < k['start']:
			start = start + datetime.timedelta(days=-1)


		end = currtime.replace(hour=k['end'],minute=0)

		if k.get('end_day_delta',False) == True:
			end = start + datetime.timedelta(days=k['end_day_delta'])

		# pprint(currtime)
		# pprint(start)
		# pprint(end)
		# pprint("--------------------------")

		# if currtime > start and currtime < end:
		if currtime >= start and currtime < end:
			candles.set_value(currtime, k['key'], True)




##########################
# Perform Volatility functions
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

vol = ['atr','natr','tr']

for index, k in enumerate(killzones):
	mask = (candles[k['key']] == True)
	df = candles[mask]
	for v in vol:
		killzones[index][v+'_mean'] = df[v].mean(skipna=True)


mask =  (
			(candles['asian_session'] == False) & 
			(candles['asian_range'] == False) & 
			(candles['asian_kill_zone'] == False) & 
			(candles['london_session'] == False) & 
			(candles['london_open_kill_zone'] == False) & 
			(candles['new_york_session'] == False) & 
			(candles['new_york_open_kill_zone'] == False)
		)
df = candles[mask]
killzones.append({ 'name': 'Non Session or Kill Zone', 'key': 'non_session_or_kill_zone' })
killzones[len(killzones)-1]['atr_mean'] = df['atr'].mean()
killzones[len(killzones)-1]['natr_mean'] = df['natr'].mean()
killzones[len(killzones)-1]['tr_mean'] = df['tr'].mean()


##########################
# Plot the data
##########################

atr_mean = []
natr_mean = []
labels = []
for k in killzones:
	labels.append(k['name'])
	atr_mean.append(k['atr_mean'])
	natr_mean.append(k['natr_mean'])



plt.rc('axes', grid=True)
plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

fig = plt.figure(facecolor='white', figsize=(11, 7), dpi=100)

# left, bottom, width, height
rect_atr = [0.1, 0.3, 0.8, 0.6]



N = len(killzones)
ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence



ax1 = fig.add_axes(rect_atr, facecolor='#f6f6f6')  
ax1.bar(ind, atr_mean, width, color='b', bottom=0) 


start = str(datetime.datetime.fromtimestamp(candles_json[len(candles_json)-1][0]/1000.0).strftime("%Y-%m-%d"))
end = str(datetime.datetime.fromtimestamp(candles_json[0][0]/1000.0).strftime("%Y-%m-%d"))
ax1.set_ylabel('ATR Value')
ax1.set_title('Average True Range, timeperiod=1, between: '+start+' and '+end, fontsize=16)
ax1.set_xticks(ind)
ax1.set_xticklabels(labels, rotation=90, fontsize=11,stretch='ultra-condensed')


im = Image.open('media/wp_logo.jpg')
# (fig.bbox.ymax - im.size[1])-20
fig.figimage(im, (fig.bbox.ymax / 2)+125, (fig.bbox.ymax - im.size[1])-10)


plt.savefig("kill_zones.png")
pprint('saved')
sys.exit()




