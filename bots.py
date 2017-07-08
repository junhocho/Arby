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

class coinone_bot:
    def __init__(self, coin, amount):
        self.alt_onetrd_amount = amount

        self.alt = coin
        self.buy_price = None
        self.sell_price = None
        self.btckrw_buy_price = None
        self.btckrw_sell_price = None
        self.altkrw_buy_price = None
        self.altkrw_sell_price = None

    def collect_price(self):
        try:
            btc_orderbook = requests.get('https://api.coinone.co.kr/orderbook/?currency=btc').json()
            alt_orderbook  = requests.get('https://api.coinone.co.kr/orderbook/?currency='+self.alt).json()
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
        while(float(alt_orderbook["ask"][count]["qty"])<self.alt_onetrd_amount):
            count+=1
        self.altkrw_buy_price = float(alt_orderbook["ask"][count]["price"])

        # BTC sell -> TAR buy
        self.altbtc_buy_price = self.altkrw_buy_price/self.btckrw_sell_price

        count = 0
        while(float(alt_orderbook["bid"][count]["qty"])<self.alt_onetrd_amount):
            count+=1
        self.altkrw_sell_price = float(alt_orderbook["bid"][count]["price"])
        # BTC buy -> TAR sell
        self.altbtc_sell_price = self.altkrw_sell_price/self.btckrw_buy_price

class korbit_bot:
    def __init__(self, coin, amount):
        self.alt_onetrd_amount = amount

        self.alt = coin
        self.buy_price = None
        self.sell_price = None
        self.btckrw_buy_price = None
        self.btckrw_sell_price = None
        self.altkrw_buy_price = None
        self.altkrw_sell_price = None

    def collect_price(self):
        #try:
        btc_orderbook = requests.get('https://api.korbit.co.kr/v1/orderbook?currency_pair=btc_krw').json()
        alt_orderbook  = requests.get('https://api.korbit.co.kr/v1/orderbook?currency_pair='+ self.alt.lower()+'_krw').json()
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
        while(float(alt_orderbook["asks"][count][1])<self.alt_onetrd_amount): # quantity
            count+=1
        self.altkrw_buy_price = float(alt_orderbook["asks"][count][0])

        # BTC sell -> TAR buy
        self.altbtc_buy_price = self.altkrw_buy_price/self.btckrw_sell_price

        count = 0
        while(float(alt_orderbook["bids"][count][1])<self.alt_onetrd_amount):
            count+=1
        self.altkrw_sell_price = float(alt_orderbook["bids"][count][0])
        # BTC buy -> TAR sell
        self.altbtc_sell_price = self.altkrw_sell_price/self.btckrw_buy_price


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
        self.buy_order = 0 ## TODO : Do we need?
        self.sell_order = 0

        self.fee_trd = 0.075 # percentage. Use coupon!
        self.fee_btc_tx = 0.0005 # BTC  1500
        self.fee_alt_tx = 0.01 # LTC  600

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
        self.btc_with_daily_limit = 150
        self.btc_with_min = 0.001

        self.alt_with_daily_amount = 0 # LTC : 1500 once / 10000 daily
        self.alt_with_daily_limit = 1500
        self.alt_with_daily_limit = 10000
        self.alt_with_min = 0.01

        self.today = datetime.now().day

    def collect_price(self):
        btc_orderbook = requests.get('https://api.bithumb.com/public/orderbook/BTC').json()
        # TODO : BTC amount limit??
        # TODO : Bithumb need to check BTC amount too.
        self.btckrw_buy_price = float(btc_orderbook["data"]["asks"][0]["price"])
        self.btckrw_sell_price = float(btc_orderbook["data"]["bids"][0]["price"])

        alt_orderbook = requests.get('https://api.bithumb.com/public/orderbook/'+ self.alt_name).json()
        count = 0
        while(float(alt_orderbook["data"]["asks"][count]["quantity"])<self.alt_onetrd_amount):
            count+=1
        self.altkrw_buy_price = float(alt_orderbook["data"]["asks"][count]["price"])
        # BTC sell -> TAR buy
        self.buy_price = self.altkrw_buy_price/self.btckrw_sell_price

        count = 0
        while(float(alt_orderbook["data"]["bids"][count]["quantity"])<self.alt_onetrd_amount):
            count+=1
        self.altkrw_sell_price = float(alt_orderbook["data"]["bids"][count]["price"])
        # BTC buy -> TAR sell
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
        if (self.today != day_server  ):
            self.today = day_server
            self.btc_with_daily_amount = 0
            return True
        elif self.btc_with_daily_amount < self.btc_with_daily_limit and btc_with_amount < self.btc_with_once_limit:
            return True
        else:
            return False

    def check_alt_tx_limit(self, alt_with_amount):
        # if day passed : init limit
        day_server = datetime.now().day
        if (self.today != day_server  ):
            self.today = day_server
            self.alt_with_daily_amount = 0
            return True
        elif self.alt_with_daily_amount < self.alt_with_daily_limit and alt_with_amount < self.alt_with_once_limit:
            return True
        else:
            return False

    def transact_btc2polo(self, btc_with_amount):
        # 1. check krx_bot btc account to tx
        # 2. btc_balance -= transaction + self.fee_tx
        # 3. accumulate self.btc_with_amount
        # 4. recheck balance
        t = time.time()
        if btc_with_amount < self.btc_with_min:
            raise ValueError('btc to withdrawal : {} is smaller than {}'.format(btc_with_amount), self.btc_with_min)
        print("Tx BTC : BITHUMB -> POLO")

        btc_in_tx = btc_with_amount - self.fee_btc_tx
        self.btc_balance -= btc_with_amount
        self.btc_in_tx = btc_in_tx # TODO : if krx recieved, this needs to be zero
        self.btc_with_daily_amount += btc_with_amount
        return {'time' : t, 'amount' : btc_in_tx}

    def transact_alt2polo(self, alt_with_amount):
        # 1. check krx_bot alt account to tx
        # 2. transaction - self.fee_tx
        # 3. accumulate self.btc_with_amount
        # 4. recheck balance
        t = time.time()
        if alt_with_amount < self.alt_with_min:
            raise ValueError('alt to withdrawal : {} is smaller than {}'.format(alt_with_amount, self.alt_with_min))

        print("Tx ALT : BITHUMB -> POLO")
        alt_in_tx = alt_with_amount - self.fee_alt_tx
        self.alt_balance -= alt_with_amount
        self.alt_in_tx = alt_in_tx # TODO: krx recieved -> zero
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
        self.buy_order = 0
        self.sell_order = 0
        self.orderbook = None

        self.fee_trd = 0.0025 # percentage
        self.fee_btc_tx = 0.0001 # BTC 300 krw
        self.fee_alt_tx = 0.001 # LTC 60 krw

        self.btc_balance = 0
        self.alt_balance = 0
        self.btc_trd_amount = 0 # TODO : if exceed, trade level up

        self.btc_in_tx = 0
        self.alt_in_tx = 0


        # self.btc_with_daily_amount = 0
        # self.alt_with_daily_amount = 0
        self.usd_with_daily_amount = 0
        self.usd_with_daily_limit = 2000 # daily $2,000.00 USD
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
        self.buy_order = count

        count = 0
        while(float(self.orderbook["bids"][count][1])<self.alt_onetrd_amount):
            count+=1

        self.sell_price = float(self.orderbook["bids"][count][0])
        self.sell_order = count

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

    def check_tx_limit(self):
        # if day passed : init limit
        day_server = datetime.utcnow().day
        if (self.today != day_server  ):
            self.today = day_server
            self.usd_with_daily_amount = 0
            return True
        elif self.usd_with_daily_amount < self.usd_with_daily_limit:
            return True
        else:
            return False

    def btcusd(self):
        ret = urllib.request.urlopen(urllib.request.Request('https://api.cryptowat.ch/markets/poloniex/btcusd/price'))
        return int(json.loads(ret.read())['result']['price'])

    def transact_btc2krx(self, btc_with_amount):
        # 1. check krx_bot btc account to tx
        # 2. btc_balance -= transaction + self.fee_tx
        # 3. accumulate self.btc_with_amount
        # 4. recheck balance
        t = time.time()
        btc_in_tx = btc_with_amount - self.fee_btc_tx
        if btc_in_tx < 0:
            raise ValueError('btc to withdrawal : {} is smaller than fee'.format(btc_with_amount))
        print("Tx BTC : POLO -> BITHUMB")
        self.btc_balance -= btc_with_amount
        self.btc_in_tx = btc_in_tx # TODO : if krx recieved, this needs to be zero
        self.usd_with_daily_amount += btc_with_amount * self.btcusd()
        return {'time' : t, 'amount' : btc_in_tx}


    def transact_alt2krx(self, alt_with_amount):
        # 1. check krx_bot alt account to tx
        # 2. transaction - self.fee_tx
        # 3. accumulate self.btc_with_amount
        # 4. recheck balance
        t = time.time()
        alt_in_tx = alt_with_amount - self.fee_alt_tx
        if alt_in_tx < 0:
            raise ValueError('alt to withdrawal : {} is smaller than fee'.format(alt_with_amount))
        print("Tx ALT : POLO -> BITHUMB")
        self.alt_balance -= alt_with_amount
        self.alt_in_tx = alt_in_tx # TODO: krx recieved -> zero
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
