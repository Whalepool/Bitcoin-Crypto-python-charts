#!/usr/bin/env python3

# Blah
import argparse 
import os
from os import path
import logging
import pandas as pd
import numpy as np 
import re
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

# Word cloud
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


# Configure Logging
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')
logger.info('Beginning...')


# Args  
parser = argparse.ArgumentParser()
parser.add_argument('--historical', action='store_true', help='get historical data?')
args = parser.parse_args()


# Check ENV variables
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
logger.info('Setting google trend object')
pytrend = TrendReq(os.environ.get('GUSERNAME'), os.environ.get('GPASS'), custom_useragent='Whalepool Trend Checker')

logger.info('Building google trend payload')
pytrend.build_payload(kw_list=['bitcoin'],timeframe="now 7-d")

logger.info('Getting related queries')
related = pytrend.related_queries()

text =  re.sub( "\\n[0-9]+", '', related['bitcoin']['rising']['query'].to_string() )
text =  re.sub( "[0-9]+", '', text )

logger.info('Words')
pprint(text)






d = path.dirname(__file__)


extra_stopwords = ['physique','calculator','vs','free','cuban','mark']
for e in extra_stopwords:
	STOPWORDS.add(e)

stopwords = set(STOPWORDS)
wc = WordCloud(background_color="white", max_words=2000,
               stopwords=stopwords,mode="RGBA",colormap='BuPu')
# generate word cloud
wc.generate(text)

# store to file
wc.to_file(path.join(d, "google-trends-wordcloud.png"))
pprint('saved')


sys.exit()