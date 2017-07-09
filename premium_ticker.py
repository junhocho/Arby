#! /usr/bin/env python3


#################
## Sell Expensive! And Buy Cheap!!
################

import sys
import os

import pprint
import json

from datetime import datetime
import time
# from noti.slack import SlackLogger

from bots import  bithumb_bot, poloniex_bot #coinone_bot, korbit_bot,
from Arby import Arby


threshold = 0.5 

# Setup Logger

import logging
import logging.handlers

logger = logging.getLogger('crumbs')
logger.setLevel(logging.DEBUG)

logging.getLogger("requests").setLevel(logging.WARNING)


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

#logger = SlackLogger(os.environ["BITHUMB_API_NAME"])


alt_onetrd_amount_dict = {
        "ETH": 0.2,
        "LTC": 1.0,
        "DASH": 0.25,
        "ETC": 3.0,
        "XRP": 100
        }

alt_kind_dict = ["BTC", "ETH", "LTC", "DASH", "ETC", "XRP"]


update_period = 2 # seconds

log_file = "exchange_logs/log.csv"

krx_eth_bot = bithumb_bot('ETH', alt_onetrd_amount_dict['ETH'])
krx_etc_bot = bithumb_bot('ETC', alt_onetrd_amount_dict['ETC'])
krx_ltc_bot = bithumb_bot('LTC', alt_onetrd_amount_dict['LTC'])
krx_dash_bot = bithumb_bot('DASH', alt_onetrd_amount_dict['DASH'])
krx_xrp_bot = bithumb_bot('XRP', alt_onetrd_amount_dict['XRP'])

polo_eth_bot = poloniex_bot('ETH', alt_onetrd_amount_dict['ETH'])
polo_etc_bot = poloniex_bot('ETC', alt_onetrd_amount_dict['ETC'])
polo_ltc_bot = poloniex_bot('LTC', alt_onetrd_amount_dict['LTC'])
polo_dash_bot = poloniex_bot('DASH', alt_onetrd_amount_dict['DASH'])
polo_xrp_bot = poloniex_bot('XRP', alt_onetrd_amount_dict['XRP'])

polo_eth_bot.collect_price()
polo_etc_bot.collect_price()
polo_ltc_bot.collect_price()
polo_dash_bot.collect_price()
polo_xrp_bot.collect_price()

Arby_eth = Arby(polo_eth_bot, krx_eth_bot)
Arby_etc = Arby(polo_etc_bot, krx_etc_bot)
Arby_ltc = Arby(polo_ltc_bot, krx_ltc_bot)
Arby_dash = Arby(polo_dash_bot, krx_dash_bot)
Arby_xrp = Arby(polo_xrp_bot, krx_xrp_bot)

#################################################


### START arbitrage!!

iter_arb = 0


def wait(iter_s):
    global iter_arb
    iter_duration = time.time() - iter_s
    iter_arb+=1
    tsleep = max([update_period-iter_duration, 0])
    time.sleep(tsleep)
    iter_end = time.time()
    print('time step : '+ str(iter_end - iter_s))
    iter_s = iter_end


time_arbstart = time.time()
while(True):
    tic = time.time()

    try:
        krx_eth_bot.collect_price()
        polo_eth_bot.collect_price()
        krx_etc_bot.collect_price()
        polo_etc_bot.collect_price()
        krx_ltc_bot.collect_price()
        polo_ltc_bot.collect_price()
        krx_dash_bot.collect_price()
        polo_dash_bot.collect_price()
        krx_xrp_bot.collect_price()
        polo_xrp_bot.collect_price()
    except Exception as e:
        logger.exception("waiting next iter")
        continue
    prem_eth = Arby_eth.ticker_premium(threshold)
    prem_etc = Arby_etc.ticker_premium(threshold)
    prem_ltc = Arby_ltc.ticker_premium(threshold)
    prem_dash = Arby_dash.ticker_premium(threshold)
    prem_xrp = Arby_xrp.ticker_premium(threshold)

    # Arby_eth.calculate_premium(iter_arb, threshold)
    # Arby_etc.calculate_premium(iter_arb, threshold)
    # Arby_ltc.calculate_premium(iter_arb, threshold)
    # Arby_dash.calculate_premium(iter_arb, threshold)
    # Arby_xrp.calculate_premium(iter_arb, threshold)

    print('\t\t{}\t\t|\tPOLO\t\t|\t{}\t|\t{}\t|\t{}\t|\t{}\t|\t{}\t'
            .format('BITHUMB', 'ETH','ETC','LTC','DASH','XRP'))
    print('\t\t{} -> BTC\t|\tBTC -> {}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t'
            .format('ALT', 'ALT' , prem_eth[0], prem_etc[0], prem_ltc[0], prem_dash[0], prem_xrp[0]))
    print('\t\t{} <- BTC\t|\tBTC <- {}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t'
            .format('ALT', 'ALT' , prem_eth[1], prem_etc[1], prem_ltc[1], prem_dash[1], prem_xrp[1]))
    #iter_s= time.time()
    #wait(iter_s)
    toc = time.time()
    print(toc-tic)
