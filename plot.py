

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

# line plots

trace = dict(x=[1,2,3], y=[4,5,6], marker={'color': 'red', 'symbol': 104, 'size': "10"},
                    mode="markers+lines",  text=["one","two","three"], name='1st Trace')
layout=dict(title="First Plot", xaxis={'title':'x1'}, yaxis={'title':'x2'})

viz._send({'data': [trace], 'layout': layout, 'win': 'mywin'})


Y=np.random.rand(10)
win = viz.line(
    Y = Y
)

Z = np.append(Y, np.random.rand(10))
win = viz.line(
    Y=Z,
    win = win
)


import pandas as pd
# df = pd.DataFrame(np.random.rand(10))
# df.to_csv("file_path.csv")

alt_name = 'ETH'

X = pd.read_csv('./log/'+alt_name+'/X.csv')
Y_prem_pos = pd.read_csv("./log/"+alt_name+"/Y_prem_pos.csv")
Y_prem_neg = pd.read_csv("./log/"+alt_name+"/Y_prem_neg.csv")
Y_krx_altkrw_sell_price = pd.read_csv("./log/"+alt_name+"/Y_krx_altkrw_sell_price.csv")
Y_krx_altkrw_buy_price = pd.read_csv("./log/"+alt_name+"/Y_krx_altkrw_buy_price.csv")
Y_krx_btckrw_sell_price = pd.read_csv("./log/"+alt_name+"/Y_krx_btckrw_sell_price.csv")
Y_krx_btckrw_buy_price = pd.read_csv("./log/"+alt_name+"/Y_krx_btckrw_buy_price.csv")
Y_krx_sell_price = pd.read_csv("./log/"+alt_name+"/Y_krx_sell_price.csv")
Y_krx_buy_price = pd.read_csv("./log/"+alt_name+"/Y_krx_buy_price.csv")
Y_polo_sell_price = pd.read_csv("./log/"+alt_name+"/Y_polo_sell_price.csv")
Y_polo_buy_price = pd.read_csv("./log/"+alt_name+"/Y_polo_buy_price.csv")
Y_polo_btcusd_price = pd.read_csv("./log/"+alt_name+"/Y_polo_btcusd_price.csv")

# TODO : inconsistent length..?
X = np.array(X)[:,1]
Y_prem_pos = np.array(Y_prem_pos)[:,1]
Y_prem_neg = np.array(Y_prem_neg)[:,1]
Y_krx_altkrw_sell_price = np.array(Y_krx_altkrw_sell_price)[:,1]
Y_krx_altkrw_buy_price = np.array(Y_krx_altkrw_buy_price)[:,1]
Y_krx_btckrw_sell_price = np.array(Y_krx_btckrw_sell_price)[:,1]
Y_krx_btckrw_buy_price = np.array(Y_krx_btckrw_buy_price)[:,1]
Y_krx_sell_price = np.array(Y_krx_sell_price)[:,1]
Y_krx_buy_price = np.array(Y_krx_buy_price)[:,1]
Y_polo_sell_price = np.array(Y_polo_sell_price)[:,1]
Y_polo_buy_price = np.array(Y_polo_buy_price)[:,1]
Y_polo_btcusd_price = np.array(Y_polo_btcusd_price)[:,1]

win = viz.line(
        X=X,
        Y=Y_polo_btcusd_price
        )
