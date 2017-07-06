#! /usr/bin/env python
#
# @author	junhocho

import sys
from pprint import pprint

from secret import *

from xcoin_api_client import *
from coinone.account import Coinone
from poloniex import *

import logging
logging.getLogger("requests").setLevel(logging.WARNING)



api = XCoinAPI(BITHUMB_API_KEY, BITHUMB_API_SECRET);
my = Coinone(COINONE_API_KEY, COINONE_API_SECRET)
polo = Poloniex(POLONIEX_API_KEY, POLONIEX_API_SECRET)


## Bithumb
rgParams = {
        "order_currency" : "BTC",
        "payment_currency" : "KRW",
        };

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

# Coinone

mybal = my.balance()
coinone_balance = {}
coinone_balance['BTC'] = mybal['btc']['balance']
coinone_balance['ETC']= mybal['etc']['balance']
coinone_balance['ETH']= mybal['eth']['balance']
coinone_balance['KRW']= mybal['krw']['balance']

# Poloniex
polo_balance = polo.returnBalances()


print("==== Bith Balance ==== ")
for c in bith_balance:
    if float(bith_balance[c]) > 0:
        print(c, bith_balance[c])
print("==== Coinone Balance ==== ")
for c in coinone_balance:
    if float(coinone_balance[c]) > 0:
        print(c, coinone_balance[c])
print("==== Polo Balance ==== ")
for c in polo_balance:
    if float(polo_balance[c]) > 0:
        print(c, polo_balance[c])
#print(balance)


# or
#balance = polo('returnBalances')
#print("I have %s BTC!" % balance['BTC'])




sys.exit(0);


print("==== Polo Balance ==== ")

