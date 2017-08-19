#!/usr/bin/env python3

# Blah
import logging
import pandas as pd
from pprint import pprint
import sys
import requests
import os
import utils

import urllib.request
import json
import numpy as np

# Charting
import talib as ta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter,ScalarFormatter
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Patch
from PIL import Image

# Configure Logging
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')



SCRIPT_DIR   = os.path.dirname(os.path.realpath(__file__))
FILENAME     = SCRIPT_DIR+"/market-cap.png"
LOGO_PATH	 = SCRIPT_DIR+'/media/wp_logo.jpg'





is_billions = True
if is_billions == True:
	divide_by = 10000000000
	title = 'Billions $'
else:
	divide_by = 10000000
	title = 'Millions $'


# API URL request
url = 'https://api.coinmarketcap.com/v1/ticker/?limit=15'
request = json.loads(requests.get(url).text)

mempool = pd.DataFrame(columns=('symbol','rank','market_cap_usd','volume'))

for i in request:
	mempool.loc[i['symbol']] = [i['symbol'],i['rank'],(float(i['market_cap_usd'])/divide_by),(float(i['24h_volume_usd'])/divide_by)]


# rects1 = ax.bar(mempool.symbol.values, mempool.market_cap_usd.values, width, color='r', yerr=mempool.market_cap_usd.values)




pprint(mempool)


names = (mempool['symbol'].tolist())

n_groups = len(names)

market_cap_usd = mempool['market_cap_usd'].tolist()
volume = mempool['volume'].tolist()
index = np.arange(n_groups)
bar_width = 0.35



# Plot chart from csv
# Enable a Grid
plt.rc('axes', grid=True)
# Set Grid preferences 
plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

# Create a figure, 16 inches by 12 inches
fig = plt.figure(facecolor='white', figsize=(16, 10), dpi=120)

# Draw 3 rectangles
rect_chart = [0.05, 0.05, 0.9, 0.9]
# rect2 = [left, 0.27, width, 0.17]

ax1 = fig.add_axes(rect_chart, facecolor='#f6f6f6')  
ax2t = ax1.twinx()
ax1.set_title('Bitcoin & crypto market comparisson - whalepool.io', {'fontsize': 16, 'fontweight':300})
# x1.get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))


ax1.bar(index, market_cap_usd, bar_width,color='#552B72')
ax1.yaxis.set_major_formatter(ScalarFormatter())
ax1.set_ylabel('Market cap ('+title+')')
ax1_legend = Patch(color='#552B72', label='Market cap ('+title+')')

ax2t.bar(index + bar_width, volume, bar_width,color='#80A035')
ax1.yaxis.set_major_formatter(ScalarFormatter())
ax2t.set_ylabel('Volume ('+title+')')
ax2t_legend = Patch(color='#80A035', label='Volume ('+title+')')



plt.xticks(index + bar_width / 2, names)
plt.legend(handles=[ax1_legend,ax2t_legend])



im = Image.open(LOGO_PATH)
fig.figimage(im, 50, (fig.bbox.ymax - im.size[1])-10)

plt.savefig(FILENAME)

n = utils.Notify()
n.telegram({
		'chat_id': '@whalepoolbtcfeed',
		'message': 'Bitcoin/Crypto market caps',
		'picture': FILENAME
	})
print('Saved: '+FILENAME)
os.remove(FILENAME)
sys.exit()
