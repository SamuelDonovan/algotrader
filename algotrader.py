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
	raise Exception("Need seclogin information for trading account")

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