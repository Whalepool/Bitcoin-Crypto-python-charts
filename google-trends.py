#!/usr/bin/env python3

# Custom
import utils

# # Blah
import os
import logging
import pandas as pd
from pprint import pprint
import sys
import requests
import datetime

# # API 
import urllib.request
import json

# # Charting
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from PIL import Image

# # google Trends
from pytrends.request import TrendReq


# Configure Logging
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')
logger.info('Beginning...')


# Static Vars 
SCRIPT_DIR   = os.path.dirname(os.path.realpath(__file__))
FILENAME     = SCRIPT_DIR+"/google-trends-vs-btc.png"
GUSERNAME = os.environ.get('GUSERNAME')
GPASS     = os.environ.get('GPASS')

USER_AGENT       = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'
KEYWORD          = 'bitcoin'
TRENDS_TF        = "today 3-m"
EPOCH            = datetime.datetime.utcfromtimestamp(0)
CANDLE_TF        = '1D'
PLOT_TITLE 		 = 'Bitcoin Price / Google Trends - Whalepool.io'
LOGO_PATH		 = SCRIPT_DIR+'/media/wp_logo.jpg'

########################################################################


logger.info('Setting google trend object')
pytrend = TrendReq(GUSERNAME, GPASS, custom_useragent=USER_AGENT)

logger.info('Building google trend payload')
pytrend.build_payload(kw_list=[KEYWORD],timeframe=TRENDS_TF)

logger.info('Making interest over time dataframe')
trends = pytrend.interest_over_time()


# Get the earliest record
logger.info('Earliest dated record from trends: '+str(trends.index[0]))
trend_start_ms = (trends.index[0] - datetime.timedelta(seconds=3600))
trend_start_ms = int((trend_start_ms - EPOCH).total_seconds()  * 1000.0)


# Make Candles Request
url = 'https://api.bitfinex.com/v2/candles/trade:'+CANDLE_TF+':tBTCUSD/hist?limit=200&start='+str(trend_start_ms)
request = json.loads(requests.get(url).text)
data_set = request

# Build candles dataframe
candles = pd.read_json(json.dumps(data_set))
candles.rename(columns={0:'date', 1:'open', 2:'close', 3:'high', 4:'low', 5:'volume'}, inplace=True)
candles['date'] = pd.to_datetime( candles['date'], unit='ms' )
candles.set_index(candles['date'], inplace=True)
candles.sort_index(inplace=True)
del candles['date']
candles = candles.reset_index()[['date','open','high','low','close','volume']]
candles['date'] = candles['date'].map(mdates.date2num)


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
def fooCandlestick(ax, quotes, width=0.5, colorup='#FFA500', colordown='#222', alpha=1.0):
	OFFSET = width/2.0
	lines = []
	boxes = []

	for q in quotes:

		timestamp, op, hi, lo, close = q[:5]
		box_h = max(op, close)
		box_l = min(op, close)
		height = box_h - box_l

		if close>=op:
			color = '#3fd624'
		else:
			color = '#e83e2c'

		vline_lo = Line2D( xdata=(timestamp, timestamp), ydata=(lo, box_l), color = 'k', linewidth=0.5, antialiased=True, zorder=10 )
		vline_hi = Line2D( xdata=(timestamp, timestamp), ydata=(box_h, hi), color = 'k', linewidth=0.5, antialiased=True, zorder=10 )
		rect = Rectangle( xy = (timestamp-OFFSET, box_l), width = width, height = height, facecolor = color, edgecolor = color, zorder=10)
		rect.set_alpha(alpha)
		lines.append(vline_lo)
		lines.append(vline_hi)
		boxes.append(rect)
		ax.add_line(vline_lo)
		ax.add_line(vline_hi)
		ax.add_patch(rect)

	ax.autoscale_view()

	return lines, boxes


# Enable a Grid
plt.rc('axes', grid=True)
# Set Grid preferences 
plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

# Create a figure, 16 inches by 12 inches
fig = plt.figure(facecolor='white', figsize=(16, 10), dpi=120)

# Draw 3 rectangles
# left, bottom, width, height
rect1 = [0.05, 0.05, 0.9, 0.9]

ax1 = fig.add_axes(rect1, facecolor='#f6f6f6')  
ax1.set_xlabel('date')
ax2 = ax1.twinx()

ax1.set_title(PLOT_TITLE)
ax1.xaxis_date()

ax1.plot( trends.index.values, trends[KEYWORD].values, color='b') 
ax1.set_ylabel('trends', color='b')


fooCandlestick(ax2, candles.values, width=0.5, colorup='g', colordown='k',alpha=0.4)
ax2.set_ylabel('bitcoin price', color='g')


im = Image.open(LOGO_PATH)	
fig.figimage(   im,   105,  (fig.bbox.ymax - im.size[1])-29)

plt.savefig(FILENAME)


n = utils.Notify()
n.telegram({
		'chat_id': '@whalepoolbtcfeed',
		'message': KEYWORD+' google trends / bitcoin price',
		'picture': FILENAME
	})
print('Saved: '+FILENAME)
os.remove(FILENAME)
sys.exit()