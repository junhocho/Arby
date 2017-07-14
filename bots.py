### API calls
from xcoin_api_client import *
from coinone.account import Coinone
from poloniex import *
from secret import *

from datetime import datetime
import time

b_api = XCoinAPI(BITHUMB_API_KEY, BITHUMB_API_SECRET);
my = Coinone(COINONE_API_KEY, COINONE_API_SECRET)
p_api = Poloniex(POLONIEX_API_KEY, POLONIEX_API_SECRET)

# ========== FEE  =====
# POLO
# Maker   Taker   Trade Volume (trailing 30 day avg)
# 0.15%   0.25%   < 600 BTC <<
# 0.14%   0.24%   ≥ 600 BTC
# 0.12%   0.22%   ≥ 1,200 BTC
# 0.10%   0.20%   ≥ 2,400 BTC
# 0.08%   0.16%   ≥ 6,000 BTC
# 0.05%   0.14%   ≥ 12,000 BTC
# 0.02%   0.12%   ≥ 18,000 BTC
# 0.00%   0.10%   ≥ 24,000 BTC
# 0.00%   0.08%   ≥ 60,000 BTC
# 0.00%   0.05%   ≥ 120,000 BTC

#  OKcoin # https://www.okcoin.com/user/foreignIndex.do?random=18
# 	Level 0	Level 1	Level 2
# 200BTC 5000LTC 1000ETH

# BITHUMB : MAKER/TAKER 0.15 %
# 0.0005 BTC
# 0.01 ETC/ETH/LTC/DASH/XRP
# BITHUMB has no fee with coupon.


# 일반거래
# 레벨    최근 30일간 거래금액    Maker   Taker
# Lv.1    5,000,000원 미만        0.15%   0.15%
# Lv.2    50,000,000원 미만       0.12%   0.13%
# Lv.3    500,000,000원 미만      0.09%   0.11%  <<
# Lv.4    2,500,000,000원 미만    0.06%   0.09%
# Lv.5    10,000,000,000원 미만   0.03%   0.07%
# VIP     50,000,000,000원 미만   0%      0.05%
# VVIP    50,000,000,000원 이상   0%      0%


# fee for takers
#fee_polo = 0.0025 # Polo
# fee_coinone = 0.0011 #Lv3
# fee_bithumb = 0
# fee_korbit  = 0.0020

# fee_kor = 0
# if market_kor == 'BITHUMB':
#     fee_kor = fee_bithumb
# elif market_kor == 'COINONE':
#     fee_kor = fee_coinone
# if market_kor == 'BITHUMB':
#     fee_kor = fee_korbit


# fee_polo_tx = 0.0001
# fee_krx_tx = 0.0005


### WITHDRAWAL LIMIT
# coinone 50 BTC

#### COINONE / KORBIT future API
# btc_orderbook = requests.get('https://api.coinone.co.kr/orderbook/?currency=btc').json()
# alt_orderbook  = requests.get('https://api.coinone.co.kr/orderbook/?currency='+self.alt).json()
# btc_orderbook = requests.get('https://api.korbit.co.kr/v1/orderbook?currency_pair=btc_krw').json()
# alt_orderbook  = requests.get('https://api.korbit.co.kr/v1/orderbook?currency_pair='+ self.alt.lower()+'_krw').json()

### ==========================
# Bithumb notice
# 『Public API』
# 1초당 20회 요청 가능합니다.
# 20회 초과 요청을 보내면 API 사용이 제한되며,
# 제한 상태 해제는 관리자 승인이 필요합니다. (전화상담 요함)
#
# 『Private API』
# 1초당 10회 요청 가능합니다.
# 10회 초과 요청을 보내면 5분간 API 사용이 제한됩니다.

class bithumb_bot:
    def __init__(self, alt_name, alt_onetrd_amount):
        self.exchange_name = "BITHUMB"
        self.alt_onetrd_amount = alt_onetrd_amount

        self.alt_name = alt_name
        self.buy_price = None
        self.sell_price = None

        self.btckrw_buy_price = None
        self.btckrw_sell_price = None
        self.altkrw_buy_price = None
        self.altkrw_sell_price = None

        self.fee_trd = 0.075 # percentage. Use coupon!
        self.fee_btc_tx = 0.0005 # BTC  1500
        if alt_name == 'LTC':
            self.fee_alt_tx = 0.01 # LTC  600
            # LTC : 1500 once / 10000 daily
            self.alt_with_once_limit = 1500
            self.alt_with_daily_limit = 10000 #  10000 * 60000 / 1153 = 520,000 usd
            self.alt_with_min = 0.01
        elif alt_name == 'ETH':
            self.fee_alt_tx = 0.01
            self.alt_with_once_limit = 250
            self.alt_with_daily_limit = 1500 #  10000 * 60000 / 1153 = 520,000 usd
            self.alt_with_min = 0.01
        elif alt_name == 'ETC':
            self.fee_alt_tx = 0.01
            self.alt_with_once_limit = 5000
            self.alt_with_daily_limit = 30000 #  10000 * 60000 / 1153 = 520,000 usd
            self.alt_with_min = 0.1
        elif alt_name == 'XRP':
            self.fee_alt_tx = 0.01
            self.alt_with_once_limit = 100000
            self.alt_with_daily_limit = 50000 #  10000 * 60000 / 1153 = 520,000 usd
            self.alt_with_min = 21
        elif alt_name == 'DASH':
            self.fee_alt_tx = 0.01
            self.alt_with_once_limit = 500
            self.alt_with_daily_limit = 3000 #  10000 * 60000 / 1153 = 520,000 usd
            self.alt_with_min = 0.01

        self.btc_in_tx = 0
        self.alt_in_tx = 0
        ### BITHUMB fee_tx
        # BTC 0.0005  (3091000 * 0.0005 = 1500 krw)
        # All ALT 0.01
        # ETH 3100 krw
        # DASH 2400 krw
        # LTC 600
        # ETC 200


        self.btc_balance = 0
        self.alt_balance = 0
        self.krw_balance = 0
        self.krw_trd_amount = 0

        self.btc_with_daily_amount = 0 # BTC : 30.0005 once / 150 daily
        self.btc_with_once_limit = 30.0005
        self.btc_with_daily_limit = 150 # 150 * 3060000 / 1153 = 400,000 usd
        self.btc_with_min = 0.001

        self.alt_with_daily_amount = 0

        self.today = datetime.now().day

    def collect_price(self):
        ## ALT
        alt_orderbook = requests.get('https://api.bithumb.com/public/orderbook/'+ self.alt_name).json()
        count = 0
        while(float(alt_orderbook["data"]["asks"][count]["quantity"])<self.alt_onetrd_amount):
            count+=1
        self.altkrw_buy_price = float(alt_orderbook["data"]["asks"][count]["price"])
        # BTC sell -> TAR buy

        count = 0
        while(float(alt_orderbook["data"]["bids"][count]["quantity"])<self.alt_onetrd_amount):
            count+=1
        self.altkrw_sell_price = float(alt_orderbook["data"]["bids"][count]["price"])
        # BTC buy -> TAR sell

        ## BTC
        btc_orderbook = requests.get('https://api.bithumb.com/public/orderbook/BTC').json()
        krw_onetrd_amount = self.alt_onetrd_amount * self.altkrw_sell_price ## Assumption of KRW needed
        while(float(btc_orderbook["data"]["asks"][count]["quantity"]) < krw_onetrd_amount / float(btc_orderbook['data']['asks'][count]['price'])):
            count+=1
        self.btckrw_buy_price = float(btc_orderbook["data"]["asks"][count]["price"])


        while(float(btc_orderbook["data"]["bids"][count]["quantity"]) < krw_onetrd_amount / float(btc_orderbook['data']['bids'][count]['price'])):
            count+=1
        self.btckrw_sell_price = float(btc_orderbook["data"]["bids"][count]["price"])

        # Final sell/buy price
        self.buy_price = self.altkrw_buy_price/self.btckrw_sell_price
        self.sell_price = self.altkrw_sell_price/self.btckrw_buy_price

    # API USED
    def btc_deposit(self, depo_amount):
        self.btc_balance += depo_amount
    def btc_withdraw(self, with_amount):
        self.btc_balance -= with_amount

    def alt_deposit(self, depo_amount):
        self.alt_balance += depo_amount
    def alt_withdraw(self, with_amount):
        self.alt_balance -= with_amount

    def krw_deposit(self, depo_amount):
        self.krw_balance += depo_amount
    def krw_withdraw(self, with_amount):
        self.krw_balance -= with_amount

    def btc2alt(self): # BTC -> KRW
        btc_tosell = self.alt_onetrd_amount * self.buy_price
        #krw_needed / self.krx_bot.btckrw_buy_price
        if (self.btc_balance < btc_tosell):
            raise ValueError('BITHUMB BTC not enough : {} < {}'.format(self.btc_balance, btc_tosell))
        self.btc_balance -= btc_tosell
        self.alt_balance += self.alt_onetrd_amount
        self.krw_trd_amount += btc_tosell * self.btckrw_sell_price

    def alt2btc(self):
        if (self.alt_balance < self.alt_onetrd_amount):
            raise ValueError('BITHUMB ALT not enough : {} < {}'.format(self.alt_balance , self.alt_onetrd_amount))

        #self.krw_krx += krw_earned
        self.alt_balance -= self.alt_onetrd_amount
        #btc_earned = krw_earned / self.krx_bot.btckrw_sell_price
        btc_earned = self.alt_onetrd_amount * self.sell_price
        #self.krw_krx -= krw_earned
        self.btc_balance += btc_earned
        self.krw_trd_amount += self.alt_onetrd_amount * self.altkrw_sell_price

    def check_btc_tx_limit(self, btc_with_amount):
        # if day passed : init limit
        day_server = datetime.now().day
        if (self.today != day_server  ): # Today became Yesterday
            self.today = day_server
            self.btc_with_daily_amount = 0
            print('BITHUMB Daily BTC tx limit init')

        if self.btc_with_once_limit < btc_with_amount:
            raise ValueError('BITHUMB {} BTC tx exceeds {} once limit'
                    .format(btc_with_amount, self.btc_with_once_limit))
        elif btc_with_amount < self.btc_with_min:
            raise ValueError('btc to withdrawal : {} is smaller than {}'
                    .format(btc_with_amount, self.btc_with_min))
        elif self.btc_with_daily_limit < self.btc_with_daily_amount:
            raise ValueError('BITHUMB {} BTC today tx exceeds {} daily limit'
                    .format(self.btc_with_daily_amount, self.btc_with_daily_limit))

    def check_alt_tx_limit(self, alt_with_amount):
        # if day passed : init limit
        day_server = datetime.now().day
        if (self.today != day_server  ): # Today became Yesterday
            self.today = day_server
            self.alt_with_daily_amount = 0
            print('BITHUMB Daily ALT tx limit init')

        if self.alt_with_once_limit < alt_with_amount:
            raise ValueError('BITHUMB {} ALT tx exceeds {} once limit'
                    .format(alt_with_amount, self.alt_with_once_limit))
        elif alt_with_amount < self.alt_with_min:
            raise ValueError('alt to withdrawal : {} is smaller than {}'
                    .format(alt_with_amount, self.alt_with_min))
        elif self.alt_with_daily_limit < self.alt_with_daily_amount:
            raise ValueError('BITHUMB {} ALT today tx exceeds {} daily limit'
                    .format(self.alt_with_daily_amount, self.alt_with_daily_limit))

    def transact_btc2polo(self, btc_with_amount):
        # 1. check krx_bot btc account to tx
        # 2. btc_balance -= transaction + self.fee_tx
        # 3. accumulate self.btc_with_amount
        # 4. recheck balance
        t = time.time()
        print("Tx BTC : BITHUMB -> POLO")
        self.check_btc_tx_limit(btc_with_amount)

        btc_in_tx = btc_with_amount - self.fee_btc_tx
        self.btc_balance -= btc_with_amount
        self.btc_in_tx = btc_in_tx
        self.btc_with_daily_amount += btc_with_amount
        return {'time' : t, 'amount' : btc_in_tx}

    def transact_alt2polo(self, alt_with_amount):
        # 1. check krx_bot alt account to tx
        # 2. transaction - self.fee_tx
        # 3. accumulate self.btc_with_amount
        # 4. recheck balance
        t = time.time()
        print("Tx ALT : BITHUMB -> POLO")
        self.check_alt_tx_limit(alt_with_amount)

        alt_in_tx = alt_with_amount - self.fee_alt_tx
        self.alt_balance -= alt_with_amount
        self.alt_in_tx = alt_in_tx
        self.alt_with_daily_amount += alt_with_amount
        return {'time' : t, 'amount' : alt_in_tx}



##   POLO
class poloniex_bot:
    def __init__(self, alt_name, alt_onetrd_amount):
        self.exchange_name = "POLONIEX"
        self.alt_onetrd_amount = alt_onetrd_amount

        self.alt_name = 'BTC_'+alt_name
        self.buy_price = None
        self.sell_price = None
        self.orderbook = None

        self.fee_trd = 0.0025 # percentage
        self.fee_btc_tx = 0.0001 # BTC 300 krw
        self.fee_alt_tx = 0.001 # LTC 60 krw

        self.btc_balance = 0
        self.alt_balance = 0
        self.btc_trd_amount = 0 # TODO : if exceed, trade level up

        self.btc_in_tx = 0
        self.alt_in_tx = 0


        self.usd_with_daily_amount = 0
        self.usd_with_daily_limit = 25000 # daily $2,000.00 USD / 2nd verification 25,000 usd
        self.today = datetime.utcnow().day

    ## SIMULATION CODE

    def btc_deposit(self, depo_amount):
        self.btc_balance += depo_amount
    def btc_withdraw(self, with_amount):
        self.btc_balance -= with_amount

    def alt_deposit(self, depo_amount):
        self.alt_balance += depo_amount
    def alt_withdraw(self, with_amount):
        self.alt_balance -= with_amount


    ## Use API
    def btc_balance(self):
        return(self.btc_balance)
    def alt_balance(self):
        return(self.alt_balance)

    def detect_depo(self):
        pass

    def collect_price(self):
        self.orderbook = p_api.returnOrderBook(self.alt_name)
        count = 0
        while(float(self.orderbook["asks"][count][1])<self.alt_onetrd_amount):
            count+=1

        self.buy_price = float(self.orderbook["asks"][count][0])

        count = 0
        while(float(self.orderbook["bids"][count][1])<self.alt_onetrd_amount):
            count+=1

        self.sell_price = float(self.orderbook["bids"][count][0])

    def btc2alt(self):
        btc_needed = self.alt_onetrd_amount * (self.buy_price * (1 + self.fee_trd))
        if (self.btc_balance < btc_needed  ):
            # Not enough money to buy coin
            # return False
            raise ValueError('POLO BTC not enough : {} < {}'.format(self.btc_balance, btc_needed))
        self.btc_balance -= btc_needed
        self.alt_balance += self.alt_onetrd_amount
        self.btc_trd_amount += btc_needed

    def alt2btc(self):
        if (self.alt_balance < self.alt_onetrd_amount):
            raise ValueError('POLO ALT not enough : {} < {}'.format(self.alt_balance , self.alt_onetrd_amount))

        btc_earned = self.alt_onetrd_amount * (self.sell_price * (1 - self.fee_trd))
        self.btc_balance += btc_earned
        self.alt_balance -= self.alt_onetrd_amount
        self.btc_trd_amount += btc_earned

    def eval_alt(self, alt_amount): # Evaluate alt in btc for price now.
        return alt_amount * self.sell_price * (1 - self.fee_trd)


    def check_usd_tx_limit(self):
        # if day passed : init limit
        day_server = datetime.utcnow().day # POLO follows UTC
        if (self.today != day_server  ): # Today became Yesterday
            self.today = day_server
            self.usd_with_daily_amount = 0
            print('POLONIEX Daily USD tx limit init')
        elif self.usd_with_daily_limit < self.usd_with_daily_amount:
            raise ValueError('POLONIEX {} USD today tx exceeds {} daily limit'
                    .format(self.usd_with_daily_amount, self.usd_with_daily_limit))

    def btcusd(self):
        ret = urllib.request.urlopen(urllib.request.Request('https://api.cryptowat.ch/markets/poloniex/btcusd/price'))
        return int(json.loads(ret.read())['result']['price'])

    def transact_btc2krx(self, btc_with_amount):
        # 1. check krx_bot btc account to tx
        # 2. btc_balance -= transaction + self.fee_tx
        # 3. accumulate self.btc_with_amount
        # 4. recheck balance
        t = time.time()
        self.check_usd_tx_limit()
        btc_in_tx = btc_with_amount - self.fee_btc_tx
        if btc_in_tx < 0:
            raise ValueError('btc to withdrawal : {} is smaller than fee'.format(btc_with_amount))
        print("Tx BTC : POLO -> BITHUMB")
        self.btc_balance -= btc_with_amount
        self.btc_in_tx = btc_in_tx
        self.usd_with_daily_amount += btc_with_amount * self.btcusd()
        return {'time' : t, 'amount' : btc_in_tx}


    def transact_alt2krx(self, alt_with_amount):
        # 1. check krx_bot alt account to tx
        # 2. transaction - self.fee_tx
        # 3. accumulate self.btc_with_amount
        # 4. recheck balance
        t = time.time()
        self.check_usd_tx_limit() # Occur ValueError
        alt_in_tx = alt_with_amount - self.fee_alt_tx
        if alt_in_tx < 0:
            raise ValueError('alt to withdrawal : {} is smaller than fee'.format(alt_with_amount))
        print("Tx ALT : POLO -> BITHUMB")
        self.alt_balance -= alt_with_amount
        self.alt_in_tx = alt_in_tx
        self.usd_with_daily_amount += self.eval_alt(alt_with_amount) * self.btcusd()
        return {'time' : t, 'amount' : alt_in_tx}

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
