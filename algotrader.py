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

# # ----------------------
# # ---- Robin Stocks ----
# # ----------------------
# login = r.login(secrets.rhlogin,secrets.rhpass)
# # print(r.get_crypto_quote('BTC'))
# # print(r.get_crypto_historicals('BTC'))
# rinfo = r.profiles.load_account_profile()
# print("Current purchasing power in robinhood =", rinfo['buying_power'])
# # Robin_stocks documentation is great!
# # Once ready to trade real money it will be easy.
# # https://www.robin-stocks.com/en/latest/robinhood.html

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
	        period = "ytd",
	
	        # fetch data by interval (including intraday if period < 60 days)
	        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
	        # (optional, default is '1d')
	        interval = "5m",
	
	        # group by ticker (to access via data['SPY'])
	        # (optional, default is 'column')
	        # group_by = 'ticker',
	
	        # adjust all OHLC automatically
	        # (optional, default is False)
	        # auto_adjust = True,
	
	        # download pre/post regular market hours data
	        # (optional, default is False)
	        # prepost = True,
	
	        # use threads for mass downloading? (True/False/Integer)
	        # (optional, default is True)
	        threads = True,
	
	        # proxy URL scheme use use when downloading?
	        # (optional, default is None)
	        proxy = None,

            rounding=True
	    )
	
	data.to_csv("BTC.csv")

# --------------------
# ---- Backtrader ----
# --------------------

import backtrader as bt
import sys  # To find out the script name (in argv[0])
import datetime
import pandas as pd

# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        # print(self.datas[0].open[0])
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f' %
                    (order.executed.price,
                     order.executed.value))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f' %
                         (order.executed.price,
                          order.executed.value))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] < self.dataclose[-1]:
                    # current close less than previous close

                    if self.dataclose[-1] < self.dataclose[-2]:
                        # previous close less than the previous close

                        # BUY, BUY, BUY!!! (with default parameters)
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])

                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

# Create a cerebro entity
cerebro = bt.Cerebro()

# Add a strategy
cerebro.addstrategy(TestStrategy)

# Set our desired cash start
starting_cash = 100000.0
cerebro.broker.setcash(starting_cash)

# Datas are in a subfolder of the samples. Need to find where the script is
# because it could have been called from anywhere
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
datapath = os.path.join(modpath, 'BTC.csv')

# Create a Data Feed
data = bt.feeds.YahooFinanceCSVData(
    dataname=datapath,
    # Do not pass values before this date
    fromdate=datetime.datetime(2022, 1, 1),
    # Do not pass values before this date
    todate=datetime.datetime(2022, 1, 6),
    # Do not pass values after this date
    reverse=False

    # datetime=0,
    # open=1,
    # high=2,
    # low=3,
    # close=4,
    # volume=5,
    # openinterest=-1
    )

# Add the Data Feed to Cerebro
cerebro.adddata(data)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.run()

# Print ending data
print("--------------------------------")
df = pd.read_csv('BTC.csv')

# Stats from the algotrader
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
percentage_change = 100*(cerebro.broker.getvalue() - starting_cash)/starting_cash
print('Percentage change using algotrader: %.2f' % percentage_change)

# Stats using a buy and hold method
starting_value = df['Open'][0]
ending_value = df['Close'][len(df)-1]
bah_percentage_change = 100*(ending_value - starting_value)/starting_value
print('Percentage using buy and hold: %.2f' % bah_percentage_change)

# cerebro.plot()