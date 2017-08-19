# Few useful bitcoin chart python files


## Get teamspeak numbers
`python get_teamspeak_numbers.py`   
Simply script to query teamspeak and fetch the number of users on teamspeak and plot into mongodb


## Google Trends Wordcloud 
![Google Trends Wordcloud](http://i.imgur.com/XxWq2BA.jpg)  
`python google-trends-wordcloud.py` - makes a chart of the related search terms for google trends related to key [bitcoin]


## Google Trends / Price 
![Google Trends](http://i.imgur.com/bvqwygY.png)  
`python google-trends.py` - builds above chart


## Killzones 
![Killzones](http://i.imgur.com/Egbe9T9.jpg)  
`python killzones.py` - measures and plots bitcoin volatility 


## Market cap / volume comparisson
![Market cap](http://i.imgur.com/1pwrL2M.png)  
`python marketcap.py` - builds above chart


## Mempool over price
![Mempool over price](http://i.imgur.com/45LtGu7.png)  
`python mempool-vs-btc.py` - builds above chart


## Price over rates
![Swap rate over price](http://i.imgur.com/buUiHxx.png)  
`python swap-rate-over-price.py --type="btc"`  
`python swap-rate-over-price.py --type="usd"`  
^ is normal
  
![Swap rate over price historical](http://i.imgur.com/LImB3NW.png)  
`python swap-rate-over-price.py --type="btc --historical"`  
`python swap-rate-over-price.py --type="usd --historical"`  
^ for historical data
