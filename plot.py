

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
df = pd.DataFrame(np.random.rand(10))
df.to_csv("file_path.csv")
