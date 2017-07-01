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

coin = 'ETC'
market_kor = 'BITHUMB'
exp_name = '1'


optLen = len(sys.argv)

if optLen == 2:
    coin = sys.argv[1]
elif optLen == 3:
    coin = sys.argv[1]
    market_kor = sys.argv[2]
elif optLen == 4:
    coin = sys.argv[1]
    market_kor = sys.argv[2]
    exp_name = sys.argv[3]

# Setup Logger

import logging
import logging.handlers

logger = logging.getLogger('crumbs')
logger.setLevel(logging.DEBUG)


#formatter
formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')


# fileHandler and StreamHandler
fileHandler = logging.FileHandler('./log/loghandler.log')
streamHandler = logging.StreamHandler()

# handler formatter
fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

# handler logging add
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

# logging
#logger.debug('debug')
#logger.debug('info')
#logger.debug('warning')
#logger.debug('error')
#logger.debug('critical')



#
#
#ema_pred_flag = 0
#
#def ema_pred(flag):
#    if flag:
#        return (ema_grad > 0  and count>60) # TODO default count 60
#    else:
#        return True


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
        "XRP": 300
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

polo_coin = 'BTC_'+coin
pform = pform_dict[coin]

# Threshold for gap price
threshold = 0.01 # 0.01

# commision for takers
commision_polo = 0.0025 # Polo

commision_coinone = 0.0011 #Lv3
commision_bithumb = 0
commision_korbit  = 0.0020

commision_kor = 0
if market_kor == 'BITHUMB':
    commision_kor = commision_bithumb
elif market_kor == 'COINONE':
    commision_kor = commision_coinone
if market_kor == 'BITHUMB':
    commision_kor = commision_korbit

# POLO
# Maker   Taker   Trade Volume (trailing 30 day avg)
# 0.15%   0.25%   < 600 BTC
# 0.14%   0.24%   ≥ 600 BTC
# 0.12%   0.22%   ≥ 1,200 BTC
# 0.10%   0.20%   ≥ 2,400 BTC
# 0.08%   0.16%   ≥ 6,000 BTC
# 0.05%   0.14%   ≥ 12,000 BTC
# 0.02%   0.12%   ≥ 18,000 BTC
# 0.00%   0.10%   ≥ 24,000 BTC
# 0.00%   0.08%   ≥ 60,000 BTC
# 0.00%   0.05%   ≥ 120,000 BTC


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
def watch_price(max_price=0, min_price=0):
    resp = requests.get("https://api.coinone.co.kr/trades/?currency=eth")
    result = resp.json()

    order = result["completeOrders"][-1]
    price = int(order["price"])
    date_now = datetime.fromtimestamp(int(order["timestamp"]))
    print("max_limit: %d\nmin_limit: %d\n" % (max_price, min_price))
    print("time: %s\nprice: %d\n" % (date_now, price))

class coinone_bot:
    def __init__(self):
        self.coin = coin
        self.buy_price = None
        self.sell_price = None
        self.btckrw_buy_price = None
        self.btckrw_sell_price = None
        self.altkrw_buy_price = None
        self.altkrw_sell_price = None

    def collect_price(self):
        try:
            btc_orderbook = requests.get('https://api.coinone.co.kr/orderbook/?currency=btc').json()
            alt_orderbook  = requests.get('https://api.coinone.co.kr/orderbook/?currency='+coin).json()
            orderbook_loaded = True
        except Exception as e:
            print("Orderbook not loaded")
            orderbook_loaded = False
        if not orderbook_loaded: return False

        #ret = urlopen(urllib.request.Request('https://api.bithumb.com/public/orderbook/BTC'))
        #btc_orderbook = json.loads(ret.read())


        # TODO : BTC amount limit??
        self.btckrw_buy_price = float(btc_orderbook["ask"][0]["price"])  # TODO : Bithumb need to check BTC amount too.
        self.btckrw_sell_price = float(btc_orderbook["bid"][0]["price"])


        count = 0
        while(float(alt_orderbook["ask"][count]["qty"])<amount):
            count+=1
        self.altkrw_buy_price = float(alt_orderbook["ask"][count]["price"])

        # BTC sell -> TAR buy
        self.altbtc_buy_price = self.altkrw_buy_price/self.btckrw_sell_price

        count = 0
        while(float(alt_orderbook["bid"][count]["qty"])<amount):
            count+=1
        self.altkrw_sell_price = float(alt_orderbook["bid"][count]["price"])
        # BTC buy -> TAR sell
        self.altbtc_sell_price = self.altkrw_sell_price/self.btckrw_buy_price

class korbit_bot:
    def __init__(self):
        self.coin = coin
        self.buy_price = None
        self.sell_price = None
        self.btckrw_buy_price = None
        self.btckrw_sell_price = None
        self.altkrw_buy_price = None
        self.altkrw_sell_price = None

    def collect_price(self):
        #try:
        btc_orderbook = requests.get('https://api.korbit.co.kr/v1/orderbook?currency_pair=btc_krw').json()
        alt_orderbook  = requests.get('https://api.korbit.co.kr/v1/orderbook?currency_pair='+coin.lower()+'_krw').json()
        #orderbook_loaded = True
        #    print("Orderbook loaded")
        #except Exception as e:
        #    print("Orderbook not loaded")
        #    orderbook_loaded = False
        #if not orderbook_loaded: return False

        # TODO : BTC amount limit??
        self.btckrw_buy_price = float(btc_orderbook["asks"][0][0]) # Price
        self.btckrw_sell_price = float(btc_orderbook["bids"][0][0])


        count = 0
        while(float(alt_orderbook["asks"][count][1])<amount): # quantity
            count+=1
        self.altkrw_buy_price = float(alt_orderbook["asks"][count][0])

        # BTC sell -> TAR buy
        self.altbtc_buy_price = self.altkrw_buy_price/self.btckrw_sell_price

        count = 0
        while(float(alt_orderbook["bids"][count][1])<amount):
            count+=1
        self.altkrw_sell_price = float(alt_orderbook["bids"][count][0])
        # BTC buy -> TAR sell
        self.altbtc_sell_price = self.altkrw_sell_price/self.btckrw_buy_price


class bithumb_bot:
    def __init__(self):
        self.coin = coin
        self.buy_price = None
        self.sell_price = None
        self.btckrw_buy_price = None
        self.btckrw_sell_price = None
        self.altkrw_buy_price = None
        self.altkrw_sell_price = None

    def collect_price(self):
        btc_orderbook = b_api.xcoinApiCall("/public/orderbook/BTC", {})
        #ret = urlopen(urllib.request.Request('https://api.bithumb.com/public/orderbook/BTC'))
        #btc_orderbook = json.loads(ret.read())


        # TODO : BTC amount limit??
        self.btckrw_buy_price = float(btc_orderbook["data"]["asks"][0]["price"])  # TODO : Bithumb need to check BTC amount too.
#         print(self.btckrw_buy_price)
        self.btckrw_sell_price = float(btc_orderbook["data"]["bids"][0]["price"])
#         print(self.btckrw_sell_price)

        alt_orderbook = b_api.xcoinApiCall("/public/orderbook/" + coin, {})

        count = 0
        while(float(alt_orderbook["data"]["asks"][count]["quantity"])<amount):
            count+=1
#         print(count)
        self.altkrw_buy_price = float(alt_orderbook["data"]["asks"][count]["price"])
#         print(altkrw_buy_price)
        # BTC sell -> TAR buy
        self.altbtc_buy_price = self.altkrw_buy_price/self.btckrw_sell_price

        count = 0
        while(float(alt_orderbook["data"]["bids"][count]["quantity"])<amount):
            count+=1
#         print(count)
        self.altkrw_sell_price = float(alt_orderbook["data"]["bids"][count]["price"])
        # BTC buy -> TAR sell
        self.altbtc_sell_price = self.altkrw_sell_price/self.btckrw_buy_price


# ======= POLO
class poloniex_bot:
    def __init__(self):
        self.buy_price = None
        self.sell_price = None
        self.buy_order = 0
        self.sell_order = 0
        self.orderbook = None


    def collect_price(self):
        self.orderbook = p_api.returnOrderBook(polo_coin)
        count = 0
        while(float(self.orderbook["asks"][count][1])<amount):
            count+=1

        self.buy_price = float(self.orderbook["asks"][count][0])
        self.buy_order = count

        count = 0
        while(float(self.orderbook["bids"][count][1])<amount):
            count+=1

        self.sell_price = float(self.orderbook["bids"][count][0])
        self.sell_order = count



if market_kor == 'COINONE':
    kor_bot = coinone_bot()
elif market_kor == 'BITHUMB':
    kor_bot = bithumb_bot()
elif market_kor == 'KORBIT':
    kor_bot = korbit_bot()
polo_bot = poloniex_bot()

def calculate_premium(count):

    #global ema
    #global ema_grad
    #global time_ema
    ################## EMA not needed ######################
    #closing_price = (polo_bot.sell_price + polo_bot.buy_price)/2
    #if(count is 0):
    #    ema = closing_price
    #    ema_grad = 0.0
    #else:
    #    ema_grad = (closing_price - ema) * multiplier(time_ema)
    #    ema = (closing_price - ema) * multiplier(time_ema) + ema


    ##### START
    #print('---------------------------------------------------')
    #print()


    # 	print('BITHUMB :  \tBUY: ', b_buy_price, '\tSELL: ', b_sell_price, '\t|')
    # 	print('POLO :   \tBUY: ', p_buy_price, '\tSELL: ', p_sell_price, '\t|')
    #print(pform.format(market_kor, kor_bot.altbtc_buy_price, kor_bot.altbtc_sell_price))
    #print(pform.format('POLONIEX', polo_bot.buy_price, polo_bot.sell_price))
    #print("Pemium monitoring: POLO : BTC->{} | BITH : {}->BTC : {:5.2f}".format(coin, coin,(kor_bot.altbtc_sell_price / polo_bot.buy_price - 1)*100))
    #print("Pemium monitoring: POLO : {}->BTC | BITH : BTC->{} : {:5.2f}".format(coin, coin, (polo_bot.sell_price / kor_bot.altbtc_buy_price - 1)*100))
    #print()
    prem = 0

    #####  Premium compare #####
    if(kor_bot.altbtc_sell_price > polo_bot.buy_price * (1 + commision_polo + threshold)): # TODO Threshold : ratio? or delta?
        #### POLO : BTC -> Target   /    BITHUMB :  Taret -> BTC
        #print('#################### PREMIUM ALERT ####################\a')
        #print()
        print('\tPOLO : BTC -> {}   /    {} :  {} -> BTC'.format(coin,market_kor,coin))
        print('\tPREM RATIO: ', (kor_bot.altbtc_sell_price / polo_bot.buy_price -1 )*100, ' %')
        prem = 1
    if(polo_bot.sell_price * (1 - commision_polo - threshold) > kor_bot.altbtc_buy_price): # Each market threshold need comission
        #### POLO : Target -> BTC   /    BITHUMB :  BTC -> Target
        #print('#################### PREMIUM ALERT ####################\a')
        #print()
        print('\tPOLO : {} -> BTC   /    {} :  BTC -> {}'.format(coin,market_kor,coin))
        print('\tPREM RATIO: ', (polo_bot.sell_price / kor_bot.altbtc_buy_price - 1)*100, ' %')
        prem = -1
    #print()
    if count%10 == 0:
        usdkrw = Currency('USDKRW')
        curr = float(usdkrw.get_ask())
        ret = urlopen(urllib.request.Request('https://api.cryptowat.ch/markets/poloniex/btcusd/price'))
        btcusd = json.loads(ret.read())['result']['price']
        print("BTC premeium KRW/USD : ",str((kor_bot.btckrw_buy_price / (curr * btcusd) )), 'with btcusd =',btcusd )
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
        r = 10
        self.btc_polo = 0.1 *r # 3,360,000
        self.btc_bith = 0.1 *r# 3,360,000
        self.bith_krw = 200000*r

        if coin == 'XRP':
            self.alt_polo = 100*r #360
            self.alt_bith = 100*r
        elif coin == 'ETH':
            self.alt_polo = 1*r
            self.alt_bith = 1*r # 400,000
        elif coin == 'ETC':
            self.alt_polo = 15*r
            self.alt_bith = 15*r#26,000
        elif coin == 'LTC':
            self.alt_polo = 6*r
            self.alt_bith = 6*r # 55,800
        elif coin == 'DASH':
            self.alt_polo = 1.5*r
            self.alt_bith = 1.5*r #230,000

        self.btc_init = self.btc_polo + self.btc_bith
        self.alt_init = self.alt_polo + self.alt_bith
        self.btcsum_init = self.asset_in_btc()
        self.btc_ratio = 1
        self.alt_ratio = 1

        self.prem_pos = 0
        self.prem_neg = 0
        self.prem_pos_failed = 0
        self.prem_neg_failed = 0
        self.reallo = 0

        self.polo_trade_amount = 0 # in BTC
        self.bithum_trade_amount = 0# in KRW


    def show_asset(self):
        print('\t==== My Wallet ====')
        print('\tPOLONIEX')
        print('\t{} : {}'.format('BTC',self.btc_polo))
        print('\t{} : {}'.format(coin, self.alt_polo))
        print('\t',market_kor)
        print('\t{} : {}'.format('BTC',self.btc_bith))
        print('\t{} : {}'.format(coin,self.alt_bith))
        print('\t{} : {}'.format('KRW',self.bith_krw))
        btcsum = self.asset_in_btc()
        print('\tWorths BTC : {} \t ratio = {}'.format(btcsum, btcsum/self.btcsum_init))
        self.btc_ratio = (self.btc_polo + self.btc_bith)/self.btc_init
        self.alt_ratio = (self.alt_polo + self.alt_bith)/self.alt_init
        print('\tCoin ratio : BTC : {}\t {} : {}'.format(self.btc_ratio, coin, self.alt_ratio))
        print('\tArbitrage: +1 ({},{})\t -1 ({},{})\t Reallocate: {}\t'
                .format(self.prem_pos, self.prem_pos_failed, self.prem_neg, self.prem_neg_failed, self.reallo))
        print('\t===================')
        print()

    def asset_in_btc(self):
        total_btc = self.btc_polo + self.btc_bith + (self.alt_polo + self.alt_bith) * (polo_bot.sell_price * (1 - commision_polo))
        return total_btc

    # TODO change bith --> kormarket
    def alt_polo_buy_btc_sell(self):
        btc_needed = amount * (polo_bot.buy_price * (1 + commision_polo))

        if (self.btc_polo < btc_needed  ):
            # Not enough money to buy coin
            return False
        else:
            self.btc_polo -= btc_needed
            self.alt_polo += amount
            return True

    def alt_polo_sell_btc_buy(self):
        btc_earned = amount * (polo_bot.sell_price * (1 - commision_polo))

        if (self.alt_polo < amount):
            return False
        else:
            self.btc_polo += btc_earned
            self.alt_polo -= amount
            return True

    def alt_bith_sell_buy_btc(self):
        #krw_earned = amount * kor_bot.altkrw_sell_price #altkrw

        if (self.alt_bith < amount):
            return False
        else:
            #self.bith_krw += krw_earned
            self.alt_bith -= amount

        #btc_earned = krw_earned / kor_bot.btckrw_sell_price
        btc_earned = amount * kor_bot.altbtc_sell_price
        #self.bith_krw -= krw_earned

        self.btc_bith += btc_earned
        return True

    # TODO brain teasing. later
    def btc_bith_sell_alt_buy(self): # BTC -> KRW
        #krw_needed = amount * kor_bot.altkrw_buy_price
        btc_tosell = amount * kor_bot.altbtc_buy_price  #krw_needed / kor_bot.btckrw_buy_price

        if (self.btc_bith < btc_tosell):
            return False
        else:
            self.btc_bith -= btc_tosell
            #self.bith_krw += krw_needed

        #self.bith_krw -= krw_needed
        self.alt_bith += amount
        return True



    # BITHUMB api slower -> do first
    def bith_sell_polo_buy(self):
        if (self.alt_bith_sell_buy_btc()): # TAR->BTC
            print("BITH :",coin,"-> BTC")
        else:
            print("BITH :",coin,"-> BTC : FAILED!!!!")

        if (self.alt_polo_buy_btc_sell()): # BTC->TAR
            print("POLO : BTC ->", coin)
            return True
        else:
            print("POLO : BTC ->", coin, ": FAILED!!!!")
        return False


    def polo_sell_bith_buy(self): #1
        if (self.alt_polo_sell_btc_buy()): # TAR->BTC
            print("POLO :",coin,"-> BTC")
        else:
            print("POLO :",coin,"-> BTC : FAILED!!!!")

        if (self.btc_bith_sell_alt_buy()): # BTC->TAR# TODO  Order matters??
            print("BITH : BTC ->", coin)
            return True
        else:
            print("BITH : BTC ->", coin, ": FAILED!!!!")
        return False


    def arbitrage(self, prem_alert):
        if prem_alert == 1:
            if (self.bith_sell_polo_buy()):
                self.prem_pos += 1
            else:
                self.prem_pos_failed += 1
        elif prem_alert == -1:
            if (self.polo_sell_bith_buy()):
                self.prem_neg += 1
            else:
                self.prem_neg_failed += 1

    def asset_reallocate(self):
        btc = self.btc_polo + self.btc_bith
        alt = self.alt_polo + self.alt_bith
        self.btc_polo = btc/2
        self.btc_bith = btc/2
        self.alt_polo = alt/2
        self.alt_bith = alt/2
        self.reallo += 1



#################################################


### START arbitrage!!

iter_arb = 0
prem_alert = 0  # -1 | 0 | 1
time.sleep(update_period)


polo_bot.collect_price()
my_wallet = wallet(coin)
my_wallet.show_asset()

# TODO EMA visualize



def wait(iter_s):
    global iter_arb
    iter_duration = time.time() - iter_s
    iter_arb+=1
    tsleep = max([update_period-iter_duration, 0])
    time.sleep(tsleep)
    iter_end = time.time()
    #print('time step : '+ str(iter_end - iter_s))
    iter_s = iter_end


time_arbstart = time.time()

while(True):
    time_taken = (time.time() - time_arbstart)/60
    print("{} {} {:6} {:6.0f}m {:10.4f}\t  {}".format(market_kor, coin, iter_arb, time_taken , my_wallet.btc_ratio ,datetime.now()))
    iter_s= time.time()

    try:
        kor_bot.collect_price()
        polo_bot.collect_price()
    except Exception as e:
        #print(e)
        #print('waiting next iter')
        #logger.error( e);
        logger.exception("waiting next iter")
        wait(iter_s)
        continue

    prem_alert = calculate_premium(iter_arb)

    if prem_alert: # Prem alerted previously
        my_wallet.arbitrage(prem_alert)
        my_wallet.show_asset()
        prem_alert = 0

    if my_wallet.btc_ratio < 0.3: # or  count % 30 == 0 :
        my_wallet.asset_reallocate()
    wait(iter_s)
