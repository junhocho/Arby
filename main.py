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

import pandas as pd
import numpy as np

# Testint 1.3  1.2 0.8
#threshold = 0.09 / 100.0 # 9000 krw # EXP
#threshold = 0.5 / 100.0 # 0.01
threshold = 1.0 / 100.0 # 0.01
#t_tx = 30*60

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--alt_name', default='LTC')
parser.add_argument('--krx_name', default='BITHUMB')
parser.add_argument('--exp_name',  default='')
parser.add_argument('--mode',  default='realtime')
param = parser.parse_args()

alt_name = param.alt_name
krx_name = param.krx_name
exp_name = param.exp_name
mode = param.mode

# Setup Logger
try:
    os.mkdir('./log/'+alt_name)
except Exception:
    pass

import logging
import logging.handlers

logger = logging.getLogger('crumbs')
logger.setLevel(logging.CRITICAL)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


#formatter
formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')


# fileHandler and StreamHandler
#fileHandler = logging.FileHandler('./log/loghandler.log')
streamHandler = logging.StreamHandler()

# handler formatter
#fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

# handler logging add
#logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

#logger = SlackLogger(os.environ["BITHUMB_API_NAME"])



############### EMA INITIAL SETUP ##############

# TODO : Send LTC instead of BTC
# TODO : Telegram bot
# TODO : How to prevent ssolim
# TODO : when arb happening. set prem direction and make tx before alt/btc shortage
# TODO : Due to fee_alt_tx, last sell is little bit less than onetrd_amount. Just sell all left.
# TODO : When prem exceeds, wait for reverse prem > 0 and exchange.
# TODO : USD limit reached, gets over at final with.
# TODO : alt_in_tx, btc_in_tx   visualize
# TODO : visualize with visdom
# TODO : avoid pending. Use LTC / DASH ? fast transactions
# TODO : check daily transaction limit in check_transaction
# TODO : SIMULATION. usd with limit

alt_onetrd_amount_dict = {
        "BTC": 0.03,
        "ETH": 0.2,
        "LTC": 1.0,
        "DASH": 0.25,
        "ETC": 3.0,
        "XRP": 60
        }

alt_name_dict = ["BTC", "ETH", "LTC", "DASH", "ETC", "XRP"]
polo_coin_dict = ["BTC_ETH", "BTC_ETC", "BTC_LTC", "BTC_DASH", "BTC_XRP"]
# pform_dict = {'ETH' : '{:12}:\t  BUY : {:10.12f} \t SELL: {:10.12f}',
#         'LTC' : '{:12}:\t  BUY : {:10.12f} \t SELL: {:10.12f}',
#         'DASH' : '{:12}:\t  BUY : {:10.12f} \t SELL: {:10.12f}',
#         'ETC' : '{:12}:\t  BUY : {:10.12f} \t SELL: {:10.12f}',
#         'XRP' : '{:12}:\t  BUY : {:10.12f} \t SELL: {:10.12f}'}
#
# pform = pform_dict[alt_name]

# Threshold for gap price




update_period = 2 # seconds
exchange_count = 0



log_file = "exchange_logs/log.csv"
alt_name_log_file = "exchange_logs/" + alt_name + "_log.csv"
alt_onetrd_amount = alt_onetrd_amount_dict[alt_name]

if krx_name == 'COINONE':
    krx_bot = coinone_bot(alt_name, alt_onetrd_amount)
elif krx_name == 'BITHUMB':
    krx_bot = bithumb_bot(alt_name, alt_onetrd_amount)
elif krx_name == 'KORBIT':
    krx_bot = korbit_bot(alt_name, alt_onetrd_amount)
polo_bot = poloniex_bot(alt_name, alt_onetrd_amount)



#################################################


### START arbitrage!!



def wait(iter_s):
    iter_duration = time.time() - iter_s
    tsleep = max([update_period-iter_duration, 0])
    time.sleep(tsleep)
    iter_end = time.time()
    #print('time step : '+ str(iter_end - iter_s))
    iter_s = iter_end


##  ====== SUMMON ARBY the Abitrage Trader
Arby = Arby(polo_bot, krx_bot, mode)

## Gain dataset
if mode == 'realtime':
    pass
    #polo_bot.collect_price()
elif mode == 'simulation':
    pass

Arby.show_asset()

time_arbstart = Arby.time_init #time.time()
iter_arb = 1
while(True):

    iter_s= time.time()

    if mode == 'realtime':
        try:
            Arby.collect_price()
        except Exception as e:
            print(e)
            wait(iter_s)
            continue
    elif mode == 'simulation':
        Arby.collect_price(mode=mode, iter_arb=iter_arb)

    prem_alert = Arby.calculate_premium(threshold)
    #prem_alert = -1

    refr = Arby.check_transaction()
    if prem_alert == 1 or prem_alert == -1: # Prem alerted previously
        success = Arby.arbitrage(prem_alert)
        if success: Arby.show_asset()
        prem_alert = 0
        time_running = (time.time() - time_arbstart)/60
        print("{} {} {:6} {:6.0f}m {:10.4f}  {:10.4f}  {:10.4f}  {}"
                .format(krx_name, alt_name, iter_arb, time_running , Arby.total_ratio ,
                    Arby.btc_ratio, Arby.alt_ratio, datetime.now()))
    # TODO time.time is not needed in simul
    elif refr:
        Arby.refresh()
        time_running = (time.time() - time_arbstart)/60
        print("{} {} {:6} {:6.0f}m {:10.4f}  {:10.4f}  {:10.4f}  {}"
                .format(krx_name, alt_name, iter_arb, time_running , Arby.total_ratio ,
                    Arby.btc_ratio, Arby.alt_ratio, datetime.now()))
        # print as : KORBIT XRP  45091   7524m     1.0179      2017-07-07 05:28:09.393301
    if mode == 'realtime':
        if(iter_arb % 100) == 0:
            Arby.log_data()
        wait(iter_s)
    elif mode == 'simulation':
        print(Arby.time_stamp)
        pass
    iter_arb+=1
