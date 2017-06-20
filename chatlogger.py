#!/usr/bin/env python3
import os, sys
import datetime
import re
import numpy as np
from pprint import pprint
import telegram
from threading import Thread
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image


# Check ENV variables are set
errors = 0 
if os.environ.get('WPLogger_Bot') is not None:
	TELEGRAM_BOT_TOKEN = os.environ.get('WPLogger_Bot')
else:
	errors += 1 
	pprint('Please set a \'WPLogger_Bot\' envionment variable.')

if errors > 0:
	sys.exit()


def make_wordcloud():
	pprint('making wordcloud...')

	now = datetime.datetime.now()
	now.strftime('%Y-%m-%d')
	date = now.strftime('%Y-%m-%d')

	# (.+)(?=:)
	usernames = []

	# : (.*)
	comments = []

	with open('logs/'+date+'.log', 'r') as f:
	# with open('logs/2017-06-16.log', 'r') as f:
		for line in f:
			username = re.findall(r"^([^:]*);*", line)
			if len(username) > 0:
				if username[0] != '':
					usernames.append(username[0])

			comment = re.findall(": (.*)", line)
			if len(comment) > 0:
				if comment[0] != '':
					comments.append(comment[0])

	pprint(usernames)

	
	d = os.path.dirname(__file__)
	extra_stopwords = ['will','lol','need','BTC','bitcoin','new','one','see','yeah','good','Im','make','now','http','https','go',
		'twitter','other','also','say']
	for e in extra_stopwords:
		STOPWORDS.add(e)

	# Usernames
	mask = np.array(Image.open(os.path.join(d, "media/wp_background_mask2.png")))

	wc = WordCloud(background_color=None, max_words=2000,mask=mask,colormap='BuPu',
	               stopwords=STOPWORDS,mode="RGBA", width=800, height=400)
	wc.generate(' '.join(usernames))
	wc.to_file(os.path.join(d, "telegram-usernames.png"))

	layer1 = Image.open(os.path.join(d, "media/wp_background.png")).convert("RGBA")
	layer2 = Image.open(os.path.join(d, "telegram-usernames.png")).convert("RGBA")

	Image.alpha_composite(layer1, layer2).save("telegram-usernames.png")



	# Comments
	wc = WordCloud(background_color="white", max_words=2000,
	               stopwords=STOPWORDS,mode="RGBA", width=800, height=400)
	wc.generate(' '.join(comments))
	wc.to_file(os.path.join(d, "telegram-comments.png"))

	sys.exit()

make_wordcloud(); sys.exit()


def echo(bot, update):
	usenrame = update.message.from_user.username 
	message = usenrame+': '+update.message.text

	now = datetime.datetime.now()
	now.strftime('%Y-%m-%d')
	date = now.strftime('%Y-%m-%d')

	with open('logs/'+date+'.log', 'a+') as f:
		f.write(message+"\n")

	pprint(message)


bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
updater = Updater(bot=bot)
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.text, echo))
updater.start_polling()
updater.idle()