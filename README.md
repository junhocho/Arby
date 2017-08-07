for raspberrypi : `sudo apt-get install libcurl4-openssl-dev`
`pip install pycurl`

recommend to install anaconda3 for easy setup.

Python3 is required. Also requires numpy, pandas

```bash
pip install pycurl requests
pip install simplejson
pip install yahoo-finance		# check USDKRW
pip install httplib2 --upgrade	# Bithumb api needs
pip install visdom 				# Visualize

mkdir log

python main.py --alt_name ETH	# activate Arbitrage
```


alt_name : ETH | ETC | DASH | LTC | XRP

# Trade fee, Tx fee and Withdraw limit

## Poloniex

### Trade fee

Maker   Taker   Trade Volume (trailing 30 day avg)
0.15%   0.25%   < 600 BTC 
0.14%   0.24%   ≥ 600 BTC
0.12%   0.22%   ≥ 1,200 BTC
0.10%   0.20%   ≥ 2,400 BTC
0.08%   0.16%   ≥ 6,000 BTC
0.05%   0.14%   ≥ 12,000 BTC
0.02%   0.12%   ≥ 18,000 BTC
0.00%   0.10%   ≥ 24,000 BTC
0.00%   0.08%   ≥ 60,000 BTC
0.00%   0.05%   ≥ 120,000 BTC

### Tx fee

BTC tx fee : 0.0001 
LTC alt fee : 0.001 


### Daily withdraw (Monthly might exist too)

Total estimitated value under

1st: 2,000 USD
2nd: 25,000 USD
3rd: 200,000 USD ( can exceed it with only to whitelisted address, needs polo contact )

## Bithumb

### Trade fee

MAKER/TAKER 0.15 %
BITHUMB has no fee with coupon.

![](https://tmmsexy.s3.amazonaws.com/imgs/2017-08-07-130354.jpg)

### Tx fee

0.0005 BTC
0.01 ETC/ETH/LTC/DASH/XRP


### Daily withdraw

![](https://tmmsexy.s3.amazonaws.com/imgs/2017-08-07-130623.jpg)


written by JunhoCho
