#!/usr/bin/env python3

# Custom
import utils

# Blah
import os
import logging
import re
import sys

# # google Trends
from pytrends.request import TrendReq

# # Word cloud
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


# Configure Logging
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')
logger.info('Beginning...')



# Static Vars 
SCRIPT_DIR   = os.path.dirname(os.path.realpath(__file__))
FILENAME     = SCRIPT_DIR+"/google-trends-wordcloud.png"
GUSERNAME    = os.environ.get('GUSERNAME')
GPASS        = os.environ.get('GPASS')

USER_AGENT       = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'
KEYWORD          = 'Bitcoin'
TRENDS_TF        = "now 7-d"
EXTRA_STOPWORDS  = ['physique','calculator','vs','free','cuban','mark']


########################################################################


# Make Trends Request
logger.info('Setting google trend object')
pytrend = TrendReq(GUSERNAME, GPASS, custom_useragent=USER_AGENT)

logger.info('Building google trend payload')
pytrend.build_payload(kw_list=[KEYWORD],timeframe=TRENDS_TF)

logger.info('Getting related queries')
related = pytrend.related_queries()

text =  re.sub( "\\n[0-9]+", '', related[KEYWORD]['rising']['query'].to_string() )
text =  re.sub( "[0-9]+", '', text )

logger.info('Words')
print(text)



#####################
# Make Word Cloud
#####################
extra_stopwords = EXTRA_STOPWORDS
for e in extra_stopwords:
	STOPWORDS.add(e)

stopwords = set(STOPWORDS)
wc = WordCloud(background_color="white", max_words=2000,
               stopwords=stopwords,mode="RGBA",colormap='BuPu')
# generate word cloud
wc.generate(text)

# store to file
wc.to_file(FILENAME)

n = utils.Notify()
n.telegram({
		'chat_id': '@whalepoolbtcfeed',
		'message': KEYWORD+' related google trends for the last 7 days',
		'picture': FILENAME
	})
print('Saved: '+FILENAME)
os.remove(FILENAME)
sys.exit()