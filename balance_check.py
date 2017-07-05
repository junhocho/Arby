#! /usr/bin/env python
# XCoin API-call sample script (for Python 3.X)
#
# @author	btckorea
# @date	2017-04-11
#
#
# First, Build and install pycurl with the following commands::
# (if necessary, become root)
#
# https://pypi.python.org/pypi/pycurl/7.43.0#downloads
#
# tar xvfz pycurl-7.43.0.tar.gz
# cd pycurl-7.43.0
# python setup.py --libcurl-dll=libcurl.so install
# python setup.py --with-openssl install
# python setup.py install

import sys
from xcoin_api_client import *
import pprint
import os

b_api_key = os.environ["BITHUMB_API_KEY"]
b_api_secret = os.environ["BITHUMB_API_SECRET"]

p_api_key = os.environ["POLONIEX_API_KEY"]
p_api_secret = os.environ["POLONIEX_API_SECRET"]

api = XCoinAPI(b_api_key, b_api_secret);

rgParams = {
        "order_currency" : "BTC",
        "payment_currency" : "KRW",
        };


#
# public api
#
# /public/ticker
# /public/recent_ticker
# /public/orderbook
# /public/recent_transactions

#result = api.xcoinApiCall("/public/ticker", rgParams);
##print(result)
#print("status: " + result["status"]);
#print("last: " + result["data"]["closing_price"]);
#print("sell: " + result["data"]["sell_price"]);
#print("buy: " + result["data"]["buy_price"]);


#
# private api
#
# endpoint		=> parameters
# /info/current
# /info/account
# /info/balance
# /info/wallet_address

#rgParams = {
#        "currency" : "LTC"
#        };
#result = api.xcoinApiCall("/info/account", rgParams);
#print(result)
#print("status: " + result["status"]);
#print("created: " + result["data"]["created"]);
#print("account id: " + result["data"]["account_id"]);
#print("trade fee: " + result["data"]["trade_fee"]);
#print("balance: " + result["data"]["balance"]);
#
#
### Wallet address
#rgParams = {
#        "currency" : "BTC"
#        };
#result = api.xcoinApiCall("/info/wallet_address", rgParams);
##print(result)

## BALANCE
print("==== Bith Balance ==== ")
bith_balance = {}

coins = ["BTC", "ETH", "ETC", "LTC", "XRP"]
for c in coins:
    rgParams = {
            "currency" : c};
    result = api.xcoinApiCall("/info/balance", rgParams);
    #print(result)
    bith_balance[c] = result['data']['available_'+c.lower()]
    #print("{} :\t {}".format(c, result['data']['available_'+c.lower()]))
bith_balance['KRW'] = result['data']['available_krw']

for c in bith_balance:
    if float(bith_balance[c]) > 0:
        print(c, bith_balance[c])


print("==== Polo Balance ==== ")
import poloniex
polo = poloniex.Poloniex(p_api_key, p_api_secret)
polo_balance = polo.returnBalances()

for c in polo_balance:
    if float(polo_balance[c]) > 0:
        print(c, polo_balance[c])
#print(balance)


# or
#balance = polo('returnBalances')
#print("I have %s BTC!" % balance['BTC'])



sys.exit(0);



