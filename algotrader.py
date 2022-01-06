#!/usr/bin/env python3

import robin_stocks.robinhood as r

# Secrets file is not included in the repo.
# It should contain your trading accounts email and password
# rhlogin = "full_email_address"
# rhpass = "password"
#
# Example:
# rhlogin = "john_doe@email.com"
# rhpass = "password123"

try:
	import secrets
except:
	raise Exception("Need login information for trading account")

# ----------------------
# ---- Robin Stocks ----
# ----------------------
login = r.login(secrets.rhlogin,secrets.rhpass)
# print(r.get_crypto_quote('BTC'))
# print(r.get_crypto_historicals('BTC'))
rinfo = r.profiles.load_account_profile()
print("Current purchasing power in robinhood =", rinfo['buying_power'])
# Robin_stocks documentation is great!
# Once ready to trade real money it will be easy.
# https://www.robin-stocks.com/en/latest/robinhood.html

# -----------------------
# ---- Yahoo Finance ----
# -----------------------

import yfinance as yf
# import pandas as pd
import os.path  # To manage paths

# btc = yf.Ticker("BTC-USD")

# start_date=datetime.datetime(2021, 1, 22)
# end_date=datetime.datetime(2022, 1, 3)

# data = btc.history(start=start_date, end=end_date)

if os.path.exists("BTC.csv"):
	print("Found local market data.")
else:
	
	data = yf.download(  # or pdr.get_data_yahoo(...
	        # tickers list or string as well
	        tickers = "BTC-USD",
	
	        # use "period" instead of start/end
	        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
	        # (optional, default is '1mo')
	        period = "2y",
	
	        # fetch data by interval (including intraday if period < 60 days)
	        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
	        # (optional, default is '1d')
	        interval = "1d",
	
	        # group by ticker (to access via data['SPY'])
	        # (optional, default is 'column')
	        group_by = 'ticker',
	
	        # adjust all OHLC automatically
	        # (optional, default is False)
	        auto_adjust = True,
	
	        # download pre/post regular market hours data
	        # (optional, default is False)
	        prepost = True,
	
	        # use threads for mass downloading? (True/False/Integer)
	        # (optional, default is True)
	        threads = True,
	
	        # proxy URL scheme use use when downloading?
	        # (optional, default is None)
	        proxy = None
	    )
	
	data.to_csv("BTC.csv")

# --------------------
# ---- Backtrader ----
# --------------------

import backtrader as bt
import sys  # To find out the script name (in argv[0])
import datetime

# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        if self.dataclose[0] < self.dataclose[-1]:
            # current close less than previous close

            if self.dataclose[-1] < self.dataclose[-2]:
                # previous close less than the previous close

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.buy()

# Create a cerebro entity
cerebro = bt.Cerebro()

# Add a strategy
cerebro.addstrategy(TestStrategy)

# Set our desired cash start
cerebro.broker.setcash(100000.0)

# Datas are in a subfolder of the samples. Need to find where the script is
# because it could have been called from anywhere
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
datapath = os.path.join(modpath, 'BTC.csv')

# Create a Data Feed
data = bt.feeds.YahooFinanceCSVData(
    dataname=datapath,
    # Do not pass values before this date
    fromdate=datetime.datetime(2020, 1, 6),
    # Do not pass values before this date
    todate=datetime.datetime(2022, 1, 6),
    # Do not pass values after this date
    reverse=False)

# Add the Data Feed to Cerebro
cerebro.adddata(data)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.run()

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# cerebro.plot()