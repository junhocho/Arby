# Intro

This was a experiment of Arbitrage trading between in&out of Korea.
Its simulation showed steady good profit but as exchange does not gaurantee to send cryptos in time, there's always risk.
Tried to implement real arbitrage with exchange API but stopped because of the risk.
Use it as wish.

# Setup


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

### Transaction time & confirms

1) 코인원

비트코인(BTC) : 1 confirmation
이더리움(ETH) : 72 confirmation
리플(XRP): 1 confirmation(즉시송금)
2) 빗썸

비트코인(BTC) : 1 confirmation
리플(XRP): 1 confirmation(즉시송금)
3) 코빗

비트코인(BTC) : 3 confirmation
이더리움(ETH): 45 confirmation
이더리움 클래식(ETC): 100 confirmation
리플(XRP): 1 confirmation(즉시송금)
4) 폴로닉스(poloniex)

라이트코인(LTC) : 4 confirmation
대쉬(DASH) : 6 confirmation
5) 비트렉스(bittrex)-검색함

BTC - 1 , ETH - 12, ETC - 12, LTC - 3, DASH - 3
XMR - 3 , ZEC - 3 , XRP - 5, REP - 12, DGD - 12
XAUR - 12, SNGLS - 12, HKG - 12, SWT - 12
TIME - 12, MLN - 12 , SDC - 10, DOGE - 3
NAV - 10, NXT - 4, ARDR - 4, RADS - 3, LSK - 10
CLAM - 3, VOX - 3
6) 비파이넥스(bitfinex)

BTC: 3 confirmation
ETH: 25 confirmation
ETC: 100 confirmation
Zcash: 15 confirmation
Monero: 15 confirmation
LTC: 6 confirmation
Dash: 9 confirmation
XRP: 1 confirmation
Tether: 3 confirmation
이오스(EOS) : 25 confirmation

[from blog](https://steemit.com/kr/@bonghans/2-transaction-confirmation)


written by JunhoCho

