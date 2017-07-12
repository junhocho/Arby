#! /usr/bin/env python3
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from visdom import Visdom
import numpy as np
import math
import os.path
import getpass
from sys import platform as _platform
from six.moves import urllib

viz = Visdom()

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

from multiprocessing import Pool

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

iter_ticker = 0

update_period = 5 # seconds
def wait(iter_s):
    iter_duration = time.time() - iter_s
    tsleep = max([update_period-iter_duration, 0])
    time.sleep(tsleep)
    iter_end = time.time()
    print('time step : '+ str(iter_end - iter_s))
    iter_s = iter_end


time_arbstart = time.time()
# pool = Pool()

win_ltc = None
win_eth = None
win_etc = None
win_xrp = None
win_dash = None
win_ltc_ticker = None
win_eth_ticker = None
win_etc_ticker = None
win_xrp_ticker = None
win_dash_ticker = None

Y_ltc_pos = np.zeros(0)
Y_ltc_neg = np.zeros(0)
Y_ltc_polosell = np.zeros(0)
Y_ltc_bithsell = np.zeros(0)

Y_eth_pos = np.zeros(0)
Y_eth_neg = np.zeros(0)
Y_eth_polosell = np.zeros(0)
Y_eth_bithsell = np.zeros(0)


Y_etc_pos = np.zeros(0)
Y_etc_neg = np.zeros(0)
Y_etc_polosell = np.zeros(0)
Y_etc_bithsell = np.zeros(0)

Y_xrp_pos = np.zeros(0)
Y_xrp_neg = np.zeros(0)
Y_xrp_polosell = np.zeros(0)
Y_xrp_bithsell = np.zeros(0)

Y_dash_pos = np.zeros(0)
Y_dash_neg = np.zeros(0)
Y_dash_polosell = np.zeros(0)
Y_dash_bithsell = np.zeros(0)
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
        #
        # r1 = pool.apply_async(krx_eth_bot.collect_price)
        # r2 = pool.apply_async(polo_eth_bot.collect_price)
        # r3 = pool.apply_async(krx_etc_bot.collect_price)
        # r4 = pool.apply_async(polo_etc_bot.collect_price)
        # r5 = pool.apply_async(krx_ltc_bot.collect_price)
        # r6 = pool.apply_async(polo_ltc_bot.collect_price)
        # r7 = pool.apply_async(krx_dash_bot.collect_price)
        # r8 = pool.apply_async(polo_dash_bot.collect_price)
        # r9 = pool.apply_async(krx_xrp_bot.collect_price)
        # r10 = pool.apply_async(polo_xrp_bot.collect_price)
        # a = r1.get(timeout=10)
        # a = r2.get(timeout=10)
        # a = r3.get(timeout=10)
        # a = r4.get(timeout=10)
        # a = r5.get(timeout=10)
        # a = r6.get(timeout=10)
        # a = r7.get(timeout=10)
        # a = r8.get(timeout=10)
        # a = r9.get(timeout=10)
        # a = r10.get(timeout=10)
    except Exception as e:
        logger.exception("waiting next iter")
        # Y = np.zeros(10)
        # win = viz.line(
        #     Y = Y,
        #     win = win
        # )
        continue
    else:
        prem_eth = Arby_eth.ticker_premium(threshold)
        prem_etc = Arby_etc.ticker_premium(threshold)
        prem_ltc = Arby_ltc.ticker_premium(threshold)
        prem_dash = Arby_dash.ticker_premium(threshold)
        prem_xrp = Arby_xrp.ticker_premium(threshold)

        Y_ltc_pos = np.append(Y_ltc_pos, prem_ltc[0])
        Y_ltc_neg = np.append(Y_ltc_neg, prem_ltc[1])
        Y_ltc_vis = np.column_stack((Y_ltc_pos, Y_ltc_neg))
        Y_ltc_polosell = np.append(Y_ltc_polosell, polo_ltc_bot.sell_price)
        Y_ltc_bithsell = np.append(Y_ltc_bithsell, krx_ltc_bot.sell_price)
        Y_ltc_sell = np.column_stack((Y_ltc_polosell, Y_ltc_bithsell))

        Y_eth_pos = np.append(Y_eth_pos, prem_eth[0])
        Y_eth_neg = np.append(Y_eth_neg, prem_eth[1])
        Y_eth_vis = np.column_stack((Y_eth_pos, Y_eth_neg))
        Y_eth_polosell = np.append(Y_eth_polosell, polo_eth_bot.sell_price)
        Y_eth_bithsell = np.append(Y_eth_bithsell, krx_eth_bot.sell_price)
        Y_eth_sell = np.column_stack((Y_eth_polosell, Y_eth_bithsell))

        Y_etc_pos = np.append(Y_etc_pos, prem_etc[0])
        Y_etc_neg = np.append(Y_etc_neg, prem_etc[1])
        Y_etc_vis = np.column_stack((Y_etc_pos, Y_etc_neg))
        Y_etc_polosell = np.append(Y_etc_polosell, polo_etc_bot.sell_price)
        Y_etc_bithsell = np.append(Y_etc_bithsell, krx_etc_bot.sell_price)
        Y_etc_sell = np.column_stack((Y_etc_polosell, Y_etc_bithsell))

        Y_xrp_pos = np.append(Y_xrp_pos, prem_xrp[0])
        Y_xrp_neg = np.append(Y_xrp_neg, prem_xrp[1])
        Y_xrp_vis = np.column_stack((Y_xrp_pos, Y_xrp_neg))
        Y_xrp_polosell = np.append(Y_xrp_polosell, polo_xrp_bot.sell_price)
        Y_xrp_bithsell = np.append(Y_xrp_bithsell, krx_xrp_bot.sell_price)
        Y_xrp_sell = np.column_stack((Y_xrp_polosell, Y_xrp_bithsell))

        Y_dash_pos = np.append(Y_dash_pos, prem_dash[0])
        Y_dash_neg = np.append(Y_dash_neg, prem_dash[1])
        Y_dash_vis = np.column_stack((Y_dash_pos, Y_dash_neg))
        Y_dash_polosell = np.append(Y_dash_polosell, polo_dash_bot.sell_price)
        Y_dash_bithsell = np.append(Y_dash_bithsell, krx_dash_bot.sell_price)
        Y_dash_sell = np.column_stack((Y_dash_polosell, Y_dash_bithsell))

        win_ltc = viz.line(
            Y = Y_ltc_vis,
            win = win_ltc,
            #name = '(+)',
            opts =dict(
                title = 'LTC',
                legend = ['+', '-']
            )
        )

        win_eth= viz.line(
            Y = Y_eth_vis,
            win = win_eth,
            #name = '(+)',
            opts =dict(
                title = 'ETH',
                legend = ['+', '-']
            )
        )

        win_etc = viz.line(
            Y = Y_etc_vis,
            win = win_etc,
            #name = '(+)',
            opts =dict(
                title = 'ETC',
                legend = ['+', '-']
            )
        )

        win_xrp = viz.line(
            Y = Y_xrp_vis,
            win = win_xrp,
            #name = '(+)',
            opts =dict(
                title = 'XRP',
                legend = ['+', '-']
            )
        )

        win_dash = viz.line(
            Y = Y_dash_vis,
            win = win_dash,
            #name = '(+)',
            opts =dict(
                title = 'DASH',
                legend = ['+', '-']
            )
        )
        win_ltc_ticker = viz.line(
            Y = Y_ltc_sell,
            win = win_ltc_ticker,
            opts =dict(
                title = 'LTC sell price',
                legend = ['polo', 'bith'])
        )
        win_eth_ticker = viz.line(
            Y = Y_eth_sell,
            win = win_eth_ticker,
            opts =dict(
                title = 'ETH sell price',
                legend = ['polo', 'bith'])
        )
        win_etc_ticker = viz.line(
            Y = Y_etc_sell,
            win = win_etc_ticker,
            opts =dict(
                title = 'ETC sell price',
                legend = ['polo', 'bith'])
        )
        win_xrp_ticker = viz.line(
            Y = Y_xrp_sell,
            win = win_xrp_ticker,
            opts =dict(
                title = 'XRP sell price',
                legend = ['polo', 'bith'])
        )
        win_dash_ticker = viz.line(
            Y = Y_dash_sell,
            win = win_dash_ticker,
            opts =dict(
                title = 'DASH sell price',
                legend = ['polo', 'bith'])
        )
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
    wait(tic)
    toc = time.time()
    print(toc-tic)
    iter_ticker += 1
