#! /usr/bin/env python3


#################
## Sell Expensive! And Buy Cheap!!
################

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

threshold = 0.005 # 0.01
commision = 0.004
# BITHUMB : MAKER/TAKER 0.15 %
# 0.0005 BTC
# 0.01 ETC/ETH/LTC/DASH/XRP
# BITHUMB has no fee with coupon.


# 일반거래
# 레벨    최근 30일간 거래금액    Maker   Taker
# Lv.1    5,000,000원 미만        0.15%   0.15%
# Lv.2    50,000,000원 미만       0.12%   0.13%
# Lv.3    500,000,000원 미만      0.09%   0.11%
# Lv.4    2,500,000,000원 미만    0.06%   0.09%
# Lv.5    10,000,000,000원 미만   0.03%   0.07%
# VIP     50,000,000,000원 미만   0%      0.05%
# VVIP    50,000,000,000원 이상   0%      0%



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
        self.buy_order = 0
        self.sell_order = 0
        self.polo_orderbook = None


    def collect_price(self):
        self.polo_orderbook = p_api.returnOrderBook(polo_coin)
        count = 0
        while(float(self.polo_orderbook["asks"][count][1])<amount):
            count+=1

        self.buy_price = float(self.polo_orderbook["asks"][count][0])
        self.buy_order = count

        count = 0
        while(float(self.polo_orderbook["bids"][count][1])<amount):
            count+=1

        self.sell_price = float(self.polo_orderbook["bids"][count][0])
        self.sell_order = count
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
    print(str(count)+" ema_grad :", ema_grad ," [" + coin + "] " + str(datetime.now()))
    # 	print('BITHUMB :  \tBUY: ', b_buy_price, '\tSELL: ', b_sell_price, '\t|')
    # 	print('POLO :   \tBUY: ', p_buy_price, '\tSELL: ', p_sell_price, '\t|')
    print(pform.format('BITHUMB', bith_bot.tarbtc_buy_price, bith_bot.tarbtc_sell_price))
    print(pform.format('POLONIEX', polo_bot.buy_price, polo_bot.sell_price))
    print("Pemium monitoring: POLO : BTC->{} | BITH : {}->BTC : {:5.2f}".format(coin, coin,(bith_bot.tarbtc_sell_price / polo_bot.buy_price - 1)*100))
    print("Pemium monitoring: POLO : {}->BTC | BITH : BTC->{} : {:5.2f}".format(coin, coin, (polo_bot.sell_price / bith_bot.tarbtc_buy_price - 1)*100))
    print()
    prem = 0
    if(ema_grad and count>10): # TODO default count 60
        if(bith_bot.tarbtc_sell_price > polo_bot.buy_price * (1+commision+threshold)):
            #### POLO : BTC -> Target   /    BITHUMB :  Taret -> BTC
            print('#################### PREMIUM ALERT ####################\a')
            print()
            print('\tPOLO : BTC -> {}   /    BITHUMB :  Taret -> {}'.format(coin,coin))
            print('\tPREM RATIO: ', (bith_bot.tarbtc_sell_price / polo_bot.buy_price - 1)*100, ' %')
            prem = 1
        if(polo_bot.sell_price * (1-commision-threshold) > bith_bot.tarbtc_buy_price): # Each market threshold need comission
            #### POLO : Target -> BTC   /    BITHUMB :  BTC -> Target
            print('#################### PREMIUM ALERT ####################\a')
            print()
            print('\tPOLO : {} -> BTC   /    BITHUMB :  BTC -> {}'.format(coin,coin))
            print('\tPREM RATIO: ', (polo_bot.sell_price / bith_bot.tarbtc_buy_price - 1)*100, ' %')
            prem = -1
        print()
    if count%10 == 0:
        usdkrw = Currency('USDKRW')
        curr = float(usdkrw.get_ask())
        ret = urlopen(urllib.request.Request('https://api.cryptowat.ch/markets/poloniex/btcusd/price'))
        btcusd = json.loads(ret.read())['result']['price']
        print("BTC premeium KRW/USD : ",str((bith_bot.btckrw_buy_price / (curr * btcusd) )), 'with btcusd =',btcusd )
    return prem

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
    def __init__(self,coin):
         self.polo_btc = 0.1 # 3,360,000
         self.bith_btc = 0.1 # 3,360,000
         self.bith_krw = 200,000

         self.polo_tar = 1
         self.bith_tar = 1

    def polo_tar_buy_btc_sell(self): pass
    #if (self.polo_btc < I )
    def polo_tar_sell_btc_buy(self): pass
    def bith_tar_sell(self):
        pass
    def bith_tar_buy(self):
        pass
    def bith_btc_sell(self):pass
    def bith_btc_buy(self):
        pass

    # BITHUMB api slower -> do first
    def polo_buy_bith_sell(self):
        #bith_orderbook()
        self.bith_tar_sell()
        self.bith_btc_buy()

        #polo_orderbook()
        self.polo_tar_buy_btc_sell()


    def polo_sell_bith_buy(self): #1
        #status = bith_orderbook()
        self.bith_btc_sell()
        self.bith_tar_buy()

        #status = polo_orderbook()
        self.polo_tar_sell_btc_buy()

    def arbitrage(self, prem_alert):
        if prem_alert == 1:
            self.polo_sell_bith_buy()
        elif prem_alert == -1:
            self.polo_buy_bith_sell()


#################################################
count = 0
prem_alert = 0  # -1 | 0 | 1
time.sleep(update_period)
# count +=1


my_wallet = wallet(coin)

# TODO EMA visualize
while(True):
    iter_start = time.time()

    collect_price(count)
    prem_alert = calculate_premium(count)

    my_wallet.arbitrage(prem_alert)
    if prem_alert: # Prem alerted previously
        prem_alert = 0

    iter_duration = time.time() - iter_start
    count+=1
    tsleep = max([update_period-iter_duration, 0])
    time.sleep(tsleep)
    iter_end = time.time()
    print('time step : '+ str(iter_end - iter_start))
    iter_start = iter_end
