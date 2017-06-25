#! /usr/bin/env python3

import sys
import os
from xcoin_api_client import *
import pprint
import json

import time
from datetime import datetime
# from noti.slack import SlackLogger
from poloniex import *


from yahoo_finance import Currency

coin = sys.argv[1]

b_api_key = os.environ["BITHUMB_API_KEY"]
b_api_secret = os.environ["BITHUMB_API_SECRET"]
#logger = SlackLogger(os.environ["BITHUMB_API_NAME"])

p_api_key = os.environ["POLONIEX_API_KEY"]
p_api_secret = os.environ["POLONIEX_API_SECRET"]


b_api = XCoinAPI(b_api_key, b_api_secret)
p_api = poloniex(p_api_key, p_api_secret)
############### EMA INITIAL SETUP ##############

amount_dict = {
        "BTC": 0.03,
        "ETH": 0.3,
        "LTC": 3.0,
        "DASH": 0.6,
        "ETC": 3.0,
        "XRP": 5000
        }

threshold_dict = {
        "BTC": 1000,
        "ETH": 200,
        "LTC": 20,
        "DASH": 100,
        "ETC": 20
        }

coin_dict = ["BTC", "ETH", "LTC", "DASH", "ETC", "XRP"]
polo_coin_dict = ["BTC_ETH", "BTC_ETC", "BTC_LTC", "BTC_DASH", "BTC_XRP"]
pform_dict = {'ETH' : '{:12}:\t  BUY : {:10.12f} \t SELL: {:10.12f}',
        'LTC' : '{:12}:\t  BUY : {:10.12f} \t SELL: {:10.12f}',
        'DASH' : '{:12}:\t  BUY : {:10.12f} \t SELL: {:10.12f}',
        'ETC' : '{:12}:\t  BUY : {:10.12f} \t SELL: {:10.12f}',
        'XRP' : '{:12}:\t  BUY : {:10.12f} \t SELL: {:10.12f}'}

#if len(sys.argv) < 2 or (sys.argv[1] not in coin_dict):
#    print("enter valid coin")
#    sys.exit(1)
#coin = sys.argv[1]
#polo_coin = sys.argv[2]

polo_coin = 'BTC_'+coin
pform = pform_dict[coin]

threshold = 0.01
commision = 0.004
# BITHUMB : MAKER/TAKER 0.15 %
# 0.0005 BTC
# 0.01 ETC/ETH/LTC/DASH/XRP
update_period = 10 # seconds
exchange_count = 0



log_file = "exchange_logs/log.csv"
coin_log_file = "exchange_logs/" + coin + "_log.csv"
amount = amount_dict[coin]

time_ema = 1500/update_period
last_buy_price = 0

b_transParams_BTC = {
        "apiKey" : b_api_key,
        "secretKey" : b_api_secret,
        "currency" : 'BTC',
        "units" : amount/4
        }

b_transParams_coin = {
        "apiKey" : b_api_key,
        "secretKey" : b_api_secret,
        "currency" : coin,
        "units" : amount/4
        }

b_info_orders_Params_BTC = {
        "apiKey" : b_api_key,
        "secretKey" : b_api_secret,
        "currency" : 'BTC'
        }
b_info_orders_Params_coin = {
        "apiKey" : b_api_key,
        "secretKey" : b_api_secret,
        "currency" : coin
        }
p_info_orders_Params = {
        "currencyPair" : polo_coin
        }

my_krw = 0
my_coin = 0
state = False
######################## FUNCTIONS ########################

#################################################
def multiplier(time_period):
    return 2.0 / (time_period + 1)
##################################################


class bithumb_bot:
    def __init__(self):
        self.coin = coin
        self.buy_price = None
        self.sell_price = None
        self.btckrw_buy_price = None
        self.btckrw_sell_price = None
        self.target_buy_price = None
        self.target_sell_price = None

    def collect_price(self):
        btc_orderbook = b_api.xcoinApiCall("/public/orderbook/BTC", {})


        # TODO : BTC amount limit??
        self.btckrw_buy_price = float(btc_orderbook["data"]["asks"][0]["price"])
#         print(self.btckrw_buy_price)
        self.btckrw_sell_price = float(btc_orderbook["data"]["bids"][0]["price"])
#         print(self.btckrw_sell_price)

        target_orderbook = b_api.xcoinApiCall("/public/orderbook/" + coin, {})

        count = 0
        while(float(target_orderbook["data"]["asks"][count]["quantity"])<amount):
            count+=1
#         print(count)
        tarkrw_buy_price = target_orderbook["data"]["asks"][count]["price"]
#         print(tarkrw_buy_price)
        # BTC sell -> TAR buy
        self.tarbtc_buy_price = float(tarkrw_buy_price)/self.btckrw_sell_price


        count = 0
        while(float(target_orderbook["data"]["bids"][count]["quantity"])<amount):
            count+=1
#         print(count)
        tarkrw_sell_price = target_orderbook["data"]["bids"][count]["price"]
        # BTC buy -> TAR sell
        self.tarbtc_sell_price = float(tarkrw_sell_price)/self.btckrw_buy_price
#         print(tarkrw_sell_price)

#         print(self.tarbtc_buy_price)
#         print(self.tarbtc_sell_price)
#         print(target_orderbook)

#         print(pform.format('BITHUMB',self.tarbtc_buy_price, self.tarbtc_sell_price))

# ======= POLO
class poloniex_bot:
    def __init__(self):
        self.buy_price = None
        self.sell_price = None


    def collect_price(self):
        p_price = p_api.returnOrderBook(polo_coin)
        count = 0
        while(float(p_price["asks"][count][1])<amount):
            count+=1

        self.buy_price = float(p_price["asks"][count][0])
        count = 0
        while(float(p_price["bids"][count][1])<amount):
            count+=1

        self.sell_price = float(p_price["bids"][count][0])
#         print(pform.format('POLONIEX',self.buy_price, self.sell_price))
#         print(self.buy_price)
#         print(self.sell_price)



bith_bot = bithumb_bot()
polo_bot = poloniex_bot()

def collect_price(count):
    bith_bot.collect_price()
    polo_bot.collect_price()

def calculate_premium(count):
    global ema
    global ema_grad
    global time_ema
    ##################################################
    closing_price = (polo_bot.sell_price + polo_bot.buy_price)/2
    if(count is 0):
        ema = closing_price
        ema_grad = 0.0
    else:
        ema_grad = (closing_price - ema) * multiplier(time_ema)
        ema = (closing_price - ema) * multiplier(time_ema) + ema
    ######################## PRINT ########################
    print('---------------------------------------------------')
    print()
    print(str(count)+"  [" + coin + "] " + str(datetime.now()))
    # 	print('BITHUMB :  \tBUY: ', b_buy_price, '\tSELL: ', b_sell_price, '\t|')
    # 	print('POLO :   \tBUY: ', p_buy_price, '\tSELL: ', p_sell_price, '\t|')
    print(pform.format('BITHUMB', bith_bot.tarbtc_buy_price, bith_bot.tarbtc_sell_price))
    print(pform.format('POLONIEX', polo_bot.buy_price, polo_bot.sell_price))
    if(ema_grad>0 and count>60):
        if(bith_bot.tarbtc_sell_price > polo_bot.buy_price * (1+commision+threshold)): # TODO Analyze each if
            print('#################### PREMIUM ALERT ####################\a')
            print('\tSELL BITHUMB ', coin, '\tBUY POLONIEX BTC\t')
            print('\tPREM RATIO: ', (bith_bot.tarbtc_sell_price / polo_bot.buy_price - 1)*100, ' %')
        if(polo_bot.sell_price * (1+commision+threshold) > bith_bot.tarbtc_buy_price): # Each market threshold need comission
            print('#################### PREMIUM ALERT ####################\a')
            print('\tSELL POLONIEX ', coin, '\tBUY BITHUMB BTC')
            print('\tPREM RATIO: ', (polo_bot.sell_price / bith_bot.tarbtc_buy_price - 1)*100, ' %')
    print()
    usdkrw = Currency('USDKRW')
    curr = float(usdkrw.get_ask())
    ret = urlopen(urllib.request.Request('https://api.cryptowat.ch/markets/poloniex/btcusd/price'))
    btcusd = json.loads(ret.read())['result']['price']
    print("BTC premeium KRW/USD : " + str((bith_bot.btckrw_buy_price / (curr * btcusd)  )))

#################################################
def open_order_check():
    global b_api
    global p_api
    status = False
    if(b_api.xcoinApiCall("/info/orders",b_info_orders_Params_coin)["status"] is 5600):
        status = True
    elif(b_api.xcoinApiCall("/info/orders",b_info_orders_Params_BTC)["status"] is 5600):
        status = True

####

class wallet:
    def __init__():
         self.polo_btc =1
         self.polo_tar = 1
         self.bith_btc = 1
         self.bith_krw = 1
         self.bith.tar = 1

    def polo_tar_buy_btc_sell(): pass
    def polo_tar_sell_btc_buy(): pass
    def bith_tar_sell():
        pass
    def bith_tar_buy():
        pass
    def bith_btc_sell():
        pass 
    def bith_btc_buy():
        pass

    def bith_sell_polo_buy():
        bith_orderbook()
        bith_tar_sell()
        bith_btc_buy()

        polo_orderbook()
        polo_tar_buy_btc_sell()


    def polo_sell_bith_buy(): #1
        status = polo_orderbook()
        polo_tar_sell_btc_buy()

        status = bith_orderbook()
        bith_btc_sell()
        bith_tar_buy()


#################################################
count = 0
time.sleep(update_period)
# count +=1

# TODO EMA visualize
while(True):
    iter_start = time.time()
    collect_price(count)
    calculate_premium(count)
    iter_duration = time.time() - iter_start
    count+=1
    tsleep = max([update_period-iter_duration, 0])
    time.sleep(tsleep)
    iter_end = time.time()
    print('time step : '+ str(iter_end - iter_start))
    iter_start = iter_end
