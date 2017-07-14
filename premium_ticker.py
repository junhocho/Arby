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

alt_list = ["ETH",  "ETC", "XRP", "LTC", "DASH"]


log_file = "exchange_logs/log.csv"

krx_bots = [bithumb_bot(alt, alt_onetrd_amount_dict[alt]) for alt in alt_list]
polo_bots = [poloniex_bot(alt, alt_onetrd_amount_dict[alt]) for alt in alt_list]

for bot in polo_bots:
    bot.collect_price()

Arbys = [Arby(p,k) for p,k in zip(polo_bots, krx_bots)]


#################################################


### START arbitrage!!


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

wins_prem_monitor = [None, None, None, None, None]
wins_price_ticker = [None, None, None, None, None]
win_btc_price = [None, None]

for w in wins_prem_monitor + wins_price_ticker + win_btc_price:
    viz.close(win=w)


premiums = [np.zeros(0),np.zeros(0),np.zeros(0),np.zeros(0),np.zeros(0)]
Ys_pos = [np.zeros(0),np.zeros(0),np.zeros(0),np.zeros(0),np.zeros(0)]
Ys_neg = [np.zeros(0),np.zeros(0),np.zeros(0),np.zeros(0),np.zeros(0)]
Ys_polo_pirce = [np.zeros(0),np.zeros(0),np.zeros(0),np.zeros(0),np.zeros(0)]
Ys_krx_price= [np.zeros(0),np.zeros(0),np.zeros(0),np.zeros(0),np.zeros(0)]
Ys_prems2show = [1,2,3,4,5]
Ys_price2show = [6,7,8,9,0]
polo_price = [1,2,3,4,5]
krx_price = [1,2,3,4,5]


def ticker():
    pass


iter_ticker = 0
time_stamp = 0
while(True):
    tic = time.time()

    # TODO Better loop. prevent one fail --> all fail
    try:
        for k,p in zip(krx_bots, polo_bots):
            k.collect_price()
            p.collect_price()
    except Exception as e:
        logger.exception("waiting next iter")
    else:
        krx_btc_price = np.array([(krx_bots[2].btckrw_sell_price +krx_bots[2].btckrw_buy_price)/2]) # TODO : choose middle crawled time
        for i, arby in enumerate(Arbys):
            premiums[i] = arby.calculate_premium_(threshold)
            polo_price[i] = (polo_bots[i].sell_price + polo_bots[i].buy_price)/2
            krx_price[i] = (krx_bots[i].sell_price + krx_bots[i].buy_price)/2
        for i in range(5):
            Ys_pos[i] = np.append(Ys_pos[i], premiums[i][0])
            Ys_neg[i] = np.append(Ys_neg[i], premiums[i][1])
            Ys_polo_pirce[i] = np.append(Ys_polo_pirce[i], polo_price[i])
            Ys_krx_price[i] = np.append(Ys_krx_price[i], krx_price[i])

            Ys_prems2show[i] = np.column_stack((Ys_pos[i], Ys_neg[i]))
            Ys_price2show[i] = np.column_stack((Ys_polo_pirce[i], Ys_krx_price[i]))

        curr_time = np.array([time_stamp/60.]) # per minute
        X = np.column_stack((curr_time, curr_time))
        # TODO : global timestamp how to append
        if iter_ticker ==  0:
            for i in range(5):
                wins_prem_monitor[i] = viz.line(
                    X = X,
                    Y = Ys_prems2show[i],
                    win = wins_prem_monitor[i],
                    opts =dict(
                        title = alt_list[i],
                        legend = ['+', '-']
                    )
                )
            for i in range(5):
                wins_price_ticker[i] = viz.line(
                    X = X,
                    Y = Ys_price2show[i],
                    win = wins_price_ticker[i],
                    opts =dict(
                        title = alt_list[i]+' price',
                        legend = ['polo', 'bith'])
                )


            win_btc_price[0] = viz.line(
                    X = curr_time,
                    Y = krx_btc_price,
                    win = win_btc_price[0],
                    opts = dict(title = 'BTC price')
                )
        else:
            for i in range(5):
                Y = np.column_stack((premiums[i][0], premiums[i][1]))
                viz.updateTrace(
                    X = X,
                    Y = Y,
                    win = wins_prem_monitor[i],
                )
            for i in range(5):
                Y = np.column_stack((polo_price[i], krx_price[i]))
                viz.updateTrace(
                    X = X,
                    Y = Y,
                    win = wins_price_ticker[i],
                )

            viz.updateTrace(
                X = curr_time,
                Y = krx_btc_price,
                win = win_btc_price[0],
            )


    # print('\t\t{}\t\t|\tPOLO\t\t|\t{}\t|\t{}\t|\t{}\t|\t{}\t|\t{}\t'
    #         .format('BITHUMB', 'ETH','ETC','LTC','DASH','XRP'))
    # print('\t\t{} -> BTC\t|\tBTC -> {}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t'
    #         .format('ALT', 'ALT' , prem_eth[0], prem_etc[0], prem_ltc[0], prem_dash[0], prem_xrp[0]))
    # print('\t\t{} <- BTC\t|\tBTC <- {}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t|\t{:5.2f}\t'
    #         .format('ALT', 'ALT' , prem_eth[1], prem_etc[1], prem_ltc[1], prem_dash[1], prem_xrp[1]))
    wait(tic)
    toc = time.time()
    print(toc-tic, datetime.now())
    time_stamp += toc-tic
    iter_ticker += 1
