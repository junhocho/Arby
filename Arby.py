from yahoo_finance import Currency
import urllib.request
import time
import pandas as pd
import numpy as np

def to_unix_time(dt):
    epoch =  datetime.datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000

## TODO Better init.
# ETC ETH XRP: BTC in krx. ALT in polo
class Arby:
    def __init__(self, polo_bot, krx_bot, mode = 'realtime'):
        r = 10 # 0.3~4 btc
        self.polo_bot = polo_bot
        self.krx_bot = krx_bot
        self.alt_name = krx_bot.alt_name
        self.mode = mode

        if self.alt_name == 'XRP':
            self.polo_bot.btc_deposit(0.1*r)
            self.krx_bot.btc_deposit(0.1*r)
            self.polo_bot.alt_deposit(300*r)
            self.krx_bot.alt_deposit(300*r)
            self.krx_bot.krw_deposit(200000*r)
            # self.btc_polo = 0.01 *r # 3,360,000
            # self.btc_krx = 0.19 *r# 3,360,000
            # self.btc_depo_delayed = 0
            # self.krw_krx = 200000*r
            # self.alt_polo = 100*r #360
            # self.alt_krx = 100*r
        elif self.alt_name == 'ETH':
            self.polo_bot.btc_deposit(0.1*r)
            self.krx_bot.btc_deposit(0.1*r)
            self.polo_bot.alt_deposit(1*r)
            self.krx_bot.alt_deposit(1*r)
            self.krx_bot.krw_deposit(200000*r)
            # self.btc_polo = 0.01 *r # 3,360,000
            # self.btc_krx = 0.19 *r# 3,360,000
            # self.btc_depo_delayed = 0
            # self.krw_krx = 200000*r
            # self.alt_polo = 1*r
            # self.alt_krx = 1*r # 400,000
        elif self.alt_name == 'ETC':
            self.polo_bot.btc_deposit(0.1*r)
            self.krx_bot.btc_deposit(0.1*r)
            self.polo_bot.alt_deposit(15*r)
            self.krx_bot.alt_deposit(15*r)
            self.krx_bot.krw_deposit(200000*r)
            # self.btc_polo = 0.01 *r # 3,360,000
            # self.btc_krx = 0.19 *r# 3,360,000
            # self.btc_depo_delayed = 0
            # self.krw_krx = 200000*r
            # self.alt_polo = 15*r
            # self.alt_krx = 15*r#26,000
        elif self.alt_name == 'LTC':
            self.polo_bot.btc_deposit(0.1*r)
            self.krx_bot.btc_deposit(0.1*r)
            self.polo_bot.alt_deposit(5*r)
            self.krx_bot.alt_deposit(5*r)
            self.krx_bot.krw_deposit(200000*r)
            # self.btc_polo = 0.1  # 3,360,000 #30
            # self.btc_krx = 0.1 # 3,360,000 #30
            # self.btc_depo_delayed = 0
            # self.krw_krx = 200000*r
            # self.alt_polo = 5 # 30
            # self.alt_krx = 5 # 55,800 # 30
        elif self.alt_name == 'DASH':
            self.polo_bot.btc_deposit(0.1*r)
            self.krx_bot.btc_deposit(0.1*r)
            self.polo_bot.alt_deposit(1*r)
            self.krx_bot.alt_deposit(1*r)
            self.krx_bot.krw_deposit(200000*r)
            # self.btc_polo = 0.1 *r # 3,360,000
            # self.btc_krx = 0.1 *r# 3,360,000
            # self.btc_depo_delayed = 0
            # self.krw_krx = 200000*r
            # self.alt_polo = 1.5*r
            # self.alt_krx = 1.5*r #230,000

        #self.btc_tx_delayed = 0
        #self.alt_tx_delayed = 0
        #### THIS will be changed to API. This is simulated delayed transaction.
        self.polo_btc_tx_info = None
        self.polo_alt_tx_info = None
        self.krx_btc_tx_info = None
        self.krx_alt_tx_info = None
        self.delay_tx = 8*60 # as sec



        ## Collect price
        if self.mode == 'simulation':
            self.load_data()
            self.read_data(0)
            self.time_init = self.time_stamp
        elif self.mode == 'realtime':
            self.collect_price_()

        prem = self.calculate_premium_(1000000) # impossible threshold
        self.time_init = time.time()

        ## Values to log INIT
        self.Y_prem_pos = np.array([prem[0]])
        self.Y_prem_neg = np.array([prem[1]])
        self.Y_krx_altkrw_sell_price = np.array([self.krx_bot.altkrw_sell_price])
        self.Y_krx_altkrw_buy_price = np.array([self.krx_bot.altkrw_buy_price])
        self.Y_krx_btckrw_sell_price = np.array([self.krx_bot.btckrw_sell_price])
        self.Y_krx_btckrw_buy_price = np.array([self.krx_bot.btckrw_buy_price])
        self.Y_krx_sell_price = np.array([self.krx_bot.sell_price])
        self.Y_krx_buy_price = np.array([self.krx_bot.buy_price])
        self.Y_polo_sell_price = np.array([self.polo_bot.sell_price])
        self.Y_polo_buy_price = np.array([self.polo_bot.buy_price])
        self.Y_polo_btcusd_price = np.array([self.polo_bot.btcusd])

        time_stamp = time.time() - self.time_init
        curr_time = np.array([time_stamp/60.]) # per minute
        self.X = curr_time

        ## Needs Visdom
        try:
            from visdom import Visdom
            self.viz = Visdom()
            self.viz.env = self.alt_name
            self.win_prem_ticker = None
            self.win_altbtc_ticker = None
            self.win_altkrw_ticker = None
            self.win_btckrw_ticker = None
            self.win_btcusd_ticker = None

            self.viz.close(win = self.win_prem_ticker)
            self.viz.close(win = self.win_altbtc_ticker)
            self.viz.close(win = self.win_altkrw_ticker)
            self.viz.close(win = self.win_btckrw_ticker)
            self.viz.close(win = self.win_btcusd_ticker)

            X = np.column_stack((curr_time, curr_time))
            # PREM
            self.win_prem_ticker = self.viz.line(
                    X = X,
                    Y = np.column_stack((
                        self.Y_prem_pos * 100,
                        self.Y_prem_neg * 100)),
                    win = self.win_prem_ticker,
                    opts =dict(
                        title = self.alt_name + ' Premium in BTC',
                        legend = ['+ : krx > polo', '- : polo > krx']
                        )
                    )
            # ALTBTC
            Y =  np.column_stack((
                        (self.Y_polo_buy_price + self.Y_polo_sell_price)/2,
                        (self.Y_krx_buy_price + self.Y_krx_sell_price)/2))

            self.win_altbtc_ticker = self.viz.line(
                    X = X,
                    Y = Y,
                    win = self.win_altbtc_ticker,
                    opts =dict(
                        title = self.alt_name + ' Price in BTC',
                        legend = ['POLONIEX', 'BITHUMB'])
                    )
            # ALTKRW
            self.win_altkrw_ticker = self.viz.line(
                    X = curr_time,
                    Y = np.array([(self.krx_bot.altkrw_buy_price + self.krx_bot.altkrw_buy_price)/2]),
                    win = self.win_altkrw_ticker,
                    opts =dict(
                        title = self.alt_name + ' Price in KRW',
                        legend = ['BITHUMB'])
                    )
            # BTCKRW
            self.win_btckrw_ticker = self.viz.line(
                    X = curr_time,
                    Y = np.array([(self.krx_bot.btckrw_buy_price + self.krx_bot.btckrw_buy_price)/2]),
                    win = self.win_btckrw_ticker,
                    opts =dict(
                        title = 'BTC Price in KRW',
                        legend = ['BITHUMB'])
                    )
            # BTCUSD
            self.win_btcusd_ticker = self.viz.line(
                    X = curr_time,
                    Y = np.array([self.polo_bot.btcusd]),
                    win = self.win_btcusd_ticker,
                    opts =dict(
                        title = 'BTC Price in USD',
                        legend = ['POLONIEX'])
                    )
        except ImportError:
           print('visdom not imported')
        self.btc_init = self.btc_sum()
        self.alt_init = self.alt_sum()
        self.asset_init = self.asset_in_btc()

        #self.btc_polo + self.btc_krx
        #self.alt_init = self.alt_polo + self.alt_krx
        self.eval_asset_init = self.asset_in_btc()
        self.btc_ratio = 1
        self.alt_ratio = 1
        self.total_ratio = 1

        self.prem_pos = 0
        self.prem_neg = 0
        self.prem_pos_failed = 0
        self.prem_neg_failed = 0

    def load_data(self):
        self.data_name = ['X','Y_prem_pos' , 'Y_prem_neg', 'Y_krx_altkrw_sell_price', 'Y_krx_altkrw_buy_price', 'Y_krx_btckrw_sell_price', 'Y_krx_btckrw_buy_price', 'Y_krx_sell_price', 'Y_krx_buy_price', 'Y_polo_sell_price', 'Y_polo_buy_price', 'Y_polo_btcusd_price']
        self.data_dict = dict()
        for e in self.data_name:
            self.data_dict[e] = np.array(pd.read_csv('./data/' + self.alt_name + '/' + e + '.csv'))[:,1]

    def read_data(self, iter_arb):
        self.krx_bot.altkrw_buy_price = self.data_dict['Y_krx_altkrw_buy_price'][iter_arb]
        self.krx_bot.altkrw_sell_price = self.data_dict['Y_krx_altkrw_sell_price'][iter_arb]
        self.krx_bot.btckrw_buy_price  = self.data_dict['Y_krx_btckrw_sell_price'][iter_arb]
        self.krx_bot.btckrw_sell_price = self.data_dict['Y_krx_btckrw_buy_price'][iter_arb]
        self.krx_bot.buy_price = self.data_dict['Y_krx_sell_price'][iter_arb]
        self.krx_bot.sell_price = self.data_dict['Y_krx_sell_price'][iter_arb]

        self.polo_bot.btcusd = self.data_dict['Y_polo_btcusd_price'][iter_arb]
        self.polo_bot.sell_price = self.data_dict['Y_polo_sell_price'][iter_arb]
        self.polo_bot.buy_price = self.data_dict['Y_polo_buy_price'][iter_arb]

        self.time_stamp = self.data_dict['X'][iter_arb] * 60.0



    def refresh(self):
        btcsum = self.asset_in_btc()
        self.total_ratio = btcsum / self.asset_init
        self.btc_ratio = self.btc_sum() / self.btc_init
        self.alt_ratio = self.alt_sum() / self.alt_init

    def btc_sum(self):
        return self.polo_bot.btc_balance + self.krx_bot.btc_balance + self.polo_bot.btc_in_tx + self.krx_bot.btc_in_tx
    def alt_sum(self):
        return self.polo_bot.alt_balance + self.krx_bot.alt_balance + self.polo_bot.alt_in_tx + self.krx_bot.alt_in_tx
    def asset_in_btc(self):
        total_btc =  self.btc_sum() + self.polo_bot.eval_alt(self.alt_sum())
        return total_btc
    def asset_in_usd(self):
        return asset_in_btc() * self.polo_bot.btcusd
    def asset_in_krw(self):
        return asset_in_btc() * self.krx_bot.btckrw_sell_price


    def show_asset(self):
        print('\t==== My Wallet ====')
        # print('\tPOLONIEX')
        # print('\t{} : {}'.format('BTC', self.polo_bot.btc_balance))
        # print('\t{} : {}'.format(self.alt_name, self.polo_bot.alt_balance))
        # #print('\t{} : {}'.format('BTC in transact', self.btc_tx_delayed)) # TODO :Need Direction
        # #print('\t{} : {}'.format('ALT in transact', self.alt_tx_delayed)) # TODO :Need Direction
        # print('\t', self.krx_bot.exchange_name)
        # print('\t{} : {}'.format('BTC',self.krx_bot.btc_balance))
        # print('\t{} : {}'.format(self.alt_name, self.krx_bot.alt_balance))
        # print('\t{} : {}'.format('KRW',self.krx_bot.krw_balance))
        btcsum = self.asset_in_btc()
        self.total_ratio = btcsum / self.asset_init
        print('\tWorths BTC : {} \t ratio = {}'.format(btcsum, self.total_ratio))
        self.btc_ratio = self.btc_sum() / self.btc_init
        self.alt_ratio = self.alt_sum() / self.alt_init
        print('\tCoin ratio : BTC : {}\t {} : {}'.format(self.btc_ratio, self.alt_name, self.alt_ratio))
        print('\tArbitrage : +1 ({},{})\t -1 ({},{})\t'
                .format(self.prem_pos, self.prem_pos_failed, self.prem_neg, self.prem_neg_failed))
        print('\tTrade amount : POLO : {} BTC\t {} : {} KRW'.format(self.polo_bot.btc_trd_amount, self.krx_bot.exchange_name, self.krx_bot.krw_trd_amount))
        print('\tTransaction amount : POLO {:.2f} USD\t {} : {:.6f} BTC {:.4f} {}'
                .format(self.polo_bot.usd_with_daily_amount,
                    self.krx_bot.exchange_name,
                    self.krx_bot.btc_with_daily_amount,
                    self.krx_bot.alt_with_daily_amount,
                    self.alt_name
                    ))
        print('\t===================')
        print()





    ## TODO
    ## It's important to check spending BTC first. If no BTC. Need Emergent Transfer!
    ## If, i have enough BTC:
    ##    First, ALT -> BTC.
    ## then, BTC->ALT
    ## Chekcout both ALT, BTC amount needed from my wallet for the operation.
    ## Also need to check there are enough ask orders on exchange.
    ## Sell the expensive first

    def krx_sell_polo_buy(self):
        success = True
        try:
            self.krx_bot.alt2btc() # krx : ALT -> BTC
        except ValueError as e:
            print("\t{} : {} -> BTC : FAILED!!!!"
                    .format(self.krx_bot.exchange_name, self.alt_name))
            if (self.polo_bot.alt_in_tx == 0):
                # If transaction is on going, do not transact
                try: # ALT : polo -> krx
                    self.polo_alt_tx_info = self.polo_bot.transact_alt2krx(self.polo_bot.alt_balance)
                    if self.mode == 'simulation':
                        self.polo_alt_tx_info['time'] = self.time_stamp
                except ValueError as e:
                    print(e)
            success = False

        try:
            self.polo_bot.btc2alt() # polo : BTC -> ALT
        except ValueError as e:
            print("\tPOLO : BTC -> {} : FAILED!!!!".
                    format(self.alt_name))
            if (self.krx_bot.btc_in_tx == 0):
                try: # BTC : krx -> polo
                    self.krx_btc_tx_info = self.krx_bot.transact_btc2polo(self.krx_bot.btc_balance)
                    if self.mode == 'simulation':
                        self.krx_btc_tx_info['time'] = self.time_stamp
                except ValueError as e:
                    print(e)
            success = False
        return success

    def polo_sell_krx_buy(self): #1
        success = True
        try:
            self.polo_bot.alt2btc() # polo : ALT->BTC
        except ValueError as e:
            print("\tPOLO : {} -> BTC : FAILED!!!!"
                    .format(self.alt_name))
            if (self.krx_bot.alt_in_tx == 0):
                try: # ALT : krx -> polo
                    self.krx_alt_tx_info = self.krx_bot.transact_alt2polo(self.krx_bot.alt_balance) # SEND all ALT
                    if self.mode == 'simulation':
                        self.krx_alt_tx_info['time'] = self.time_stamp
                except ValueError as e:
                    print(e)
            success = False

        try:
            self.krx_bot.btc2alt() # krx : BTC-> ALT
        except ValueError as e:
            print("\t{} : BTC -> {} : FAILED!!!!"
                    .format(self.krx_bot.exchange_name, self.alt_name))
            if (self.polo_bot.btc_in_tx == 0):
                try: # BTC : polo -> krx
                    self.polo_btc_tx_info = self.polo_bot.transact_btc2krx(self.polo_bot.btc_balance) # SEND all BTC
                    if self.mode == 'simulation':
                        self.polo_btc_tx_info['time'] = self.time_stamp
                except ValueError as e:
                    print(e)
            success = False
        return success


    def arbitrage(self, prem_alert):
        success = False
        if prem_alert == 1:
            if (self.krx_sell_polo_buy()):
                self.prem_pos += 1
                success = True
            else:
                self.prem_pos_failed += 1
        elif prem_alert == -1:
            if (self.polo_sell_krx_buy()):
                self.prem_neg += 1
                success = True
            else:
                self.prem_neg_failed += 1
        return success

    def check_transaction(self, mode = 'realtime'):
        refr = False
        if mode == 'realtime': time_now = time.time()
        elif mode == 'simulation': time_now = self.time_stamp
        if self.polo_alt_tx_info: # ALT : polo -> krx
            if time_now - self.polo_alt_tx_info['time']  > self.delay_tx:
                self.krx_bot.alt_deposit(self.polo_alt_tx_info['amount'])
                print("ALT : POLO -> {}".format(self.krx_bot.exchange_name))
                self.polo_alt_tx_info = None
                self.polo_bot.alt_in_tx = 0
                refr = True

        if self.polo_btc_tx_info: # BTC : polo -> krx
            if time_now - self.polo_btc_tx_info['time'] > self.delay_tx:
                self.krx_bot.btc_deposit(self.polo_btc_tx_info['amount'])
                print("BTC : POLO -> {}".format(self.krx_bot.exchange_name))
                self.polo_btc_tx_info = None
                self.polo_bot.btc_in_tx = 0
                refr = True

        if self.krx_alt_tx_info: # ALT : krx -> polo
            if time_now - self.krx_alt_tx_info['time'] > self.delay_tx:
                self.polo_bot.alt_deposit(self.krx_alt_tx_info['amount'])
                print("ALT : {} -> POLO".format(self.krx_bot.exchange_name))
                self.krx_alt_tx_info = None
                self.krx_bot.alt_in_tx = 0
                refr = True

        if self.krx_btc_tx_info: # BTC : polo -> krx
            if time_now - self.krx_btc_tx_info['time'] > self.delay_tx:
                self.polo_bot.btc_deposit(self.krx_btc_tx_info['amount'])
                print("BTC : {} -> POLO".format(self.krx_bot.exchange_name))
                self.krx_btc_tx_info = None
                self.krx_bot.btc_in_tx = 0
                refr = True
        return refr

    def calculate_premium_fiat():
        usdkrw = Currency('USDKRW')
        curr = float(usdkrw.get_ask())
        btcusd = self.polo_bot.btcusd
        print("\tBTC premeium KRW/USD : ",str((self.krx_bot.btckrw_buy_price / (curr * btcusd) )), 'with btcusd =',btcusd )

    def collect_price_(self, mode='realtime', iter_arb=0): # Only collect data
        if mode == 'realtime':
            self.krx_bot.collect_price()
            self.polo_bot.collect_price()
        elif mode == 'simulation':
            self.read_data(iter_arb)


    def collect_price(self, mode='realtime', iter_arb=0): # Collect data and log and visualize
        self.collect_price_(mode=mode, iter_arb=iter_arb)
        # LOG
        #Y = np.column_stack((polo_price[i], krx_price[i]))
        krx_sell_price = np.array([self.krx_bot.sell_price])
        krx_buy_price = np.array([self.krx_bot.buy_price])
        polo_sell_price = np.array([self.polo_bot.sell_price])
        polo_buy_price = np.array([self.polo_bot.buy_price])

        # also Ticker
        self.Y_krx_buy_price = np.append(self.Y_krx_buy_price, krx_buy_price)
        self.Y_krx_sell_price = np.append(self.Y_krx_sell_price, krx_sell_price)
        self.Y_polo_buy_price = np.append(self.Y_polo_buy_price, polo_buy_price)
        self.Y_polo_sell_price = np.append(self.Y_polo_sell_price, polo_sell_price)
        # side info for simulation
        self.Y_krx_altkrw_buy_price = np.append(self.Y_krx_altkrw_buy_price,
                np.array([self.krx_bot.altkrw_buy_price]))
        self.Y_krx_altkrw_sell_price = np.append(self.Y_krx_altkrw_sell_price,
                np.array([self.krx_bot.altkrw_sell_price]))
        self.Y_krx_btckrw_buy_price = np.append(self.Y_krx_btckrw_buy_price,
                np.array([self.krx_bot.btckrw_buy_price]))
        self.Y_krx_btckrw_sell_price = np.append(self.Y_krx_btckrw_sell_price,
                np.array([self.krx_bot.btckrw_sell_price]))
        btcusd = self.polo_bot.btcusd
        self.Y_polo_btcusd_price = np.append(self.Y_polo_btcusd_price,
                np.array([btcusd]))

        self.time_stamp = time.time() - self.time_init
        curr_time = np.array([self.time_stamp/60.]) # per minute
        self.X = np.append(self.X, curr_time)
        try:
            # ALTBTC
            X = np.column_stack((curr_time, curr_time))
            Y = np.column_stack((
                (polo_buy_price + polo_sell_price)/2,
                (krx_buy_price + krx_sell_price)/2)),
            self.viz.updateTrace(
                X = X,
                Y = Y[0], # TODO : Why thue fuck [0]?
                win = self.win_altbtc_ticker,
            )
            # ALTKRW
            self.viz.updateTrace(
                    X = curr_time,
                    Y = np.array([(self.krx_bot.altkrw_buy_price + self.krx_bot.altkrw_buy_price)/2]),
                    win = self.win_altkrw_ticker,
                    )
            # BTCKRW
            self.viz.updateTrace(
                    X = curr_time,
                    Y = np.array([(self.krx_bot.btckrw_buy_price + self.krx_bot.btckrw_buy_price)/2]),
                    win = self.win_btckrw_ticker,
                    )
            # BTCUSD
            self.viz.updateTrace(
                    X = curr_time,
                    Y = np.array([btcusd]),
                    win = self.win_btcusd_ticker,
                    )
        except ImportError:
            print('Visdom not imported')

    def calculate_premium_(self, threshold): # calculate premium of positive and negative
        prem_pos_r = self.krx_bot.sell_price / (self.polo_bot.buy_price * (1 + self.polo_bot.fee_trd)) -1
        prem_neg_r = self.polo_bot.sell_price * (1 - self.polo_bot.fee_trd)/ self.krx_bot.buy_price -1
        return (prem_pos_r, prem_neg_r)


    def calculate_premium(self, threshold): # cal premium and compare for arbitrage
        (prem_pos_r, prem_neg_r) = self.calculate_premium_(threshold)

        ##################
        # 	print('BITHUMB :  \tBUY: ', b_buy_price, '\tSELL: ', b_sell_price, '\t|')
        # 	print('POLO :   \tBUY: ', p_buy_price, '\tSELL: ', p_sell_price, '\t|')
        # print(pform.format(krx_name, krx_bot.buy_price, krx_bot.sell_price))
        # print(pform.format('POLONIEX', polo_bot.buy_price, polo_bot.sell_price))
        # print("\tPemium monitoring: POLO : BTC->{} | BITH : {}->BTC : {:5.2f}"
        #         .format(self.alt_name,
        #             self.alt_name,
        #             prem_pos_r * 100))
        # print("\tPemium monitoring: POLO : {}->BTC | BITH : BTC->{} : {:5.2f}"
        #         .format(self.alt_name,
        #             self.alt_name,
        #             prem_neg_r * 100))
        #print()
        #################

        prem = 0
        #####  Premium compare ###### TODO Threshold : ratio? or delta?
        if(prem_pos_r > threshold):
            #### POLO : BTC -> Target   /    BITHUMB :  Taret -> BTC
            #print('#################### PREMIUM ALERT ####################\a')
            #print()
            print('\tPREM RATIO: ', prem_pos_r * 100, ' %')
            print('\t\t\t{}\t\t|\t\t POLO'
                    .format(self.krx_bot.exchange_name))
            print('\t\t{}\t->\tBTC\t|\tBTC\t->\t{}'
                    .format(self.alt_name, self.alt_name))
            print('\t{:10.6f}\t {:10.6f}\t|{:10.6f}\t {:10.6f}'
                    .format(self.krx_bot.alt_balance, self.krx_bot.btc_balance, self.polo_bot.btc_balance, self.polo_bot.alt_balance))
            prem = 1
        if(prem_neg_r > threshold): # Each market threshold need comission
            #### POLO : Target -> BTC   /    BITHUMB :  BTC -> Target
            #print('#################### PREMIUM ALERT ####################\a')
            #print()
            #print('\tPOLO : {} -> BTC \t|\t {} :  BTC -> {}'.format(self.alt_name,
                #self.krx_bot.exchange_name, self.alt_name))
            print('\tPREM RATIO: ', prem_neg_r * 100, ' %')
            print('\t\t\t{}\t\t|\t\t POLO'
                    .format(self.krx_bot.exchange_name))
            print('\t\t{}\t<-\tBTC\t|\tBTC\t<-\t{}'
                    .format(self.alt_name, self.alt_name))
            print('\t{:10.6f}\t {:10.6f}\t|{:10.6f}\t {:10.6f}'
                    .format(self.krx_bot.alt_balance, self.krx_bot.btc_balance, self.polo_bot.btc_balance, self.polo_bot.alt_balance))
            prem = -1

        ## log
        self.Y_prem_pos = np.append(self.Y_prem_pos, prem_pos_r)
        self.Y_prem_neg = np.append(self.Y_prem_neg, prem_neg_r)
        ## Needs visdom
        try:
            curr_time = np.array([self.time_stamp/60.]) # per minute
            X = np.column_stack((curr_time, curr_time))

            Y = np.column_stack((
                np.array([prem_pos_r * 100]),
                np.array([prem_neg_r * 100])))
            self.viz.updateTrace(
                X = X,
                Y = Y,
                win = self.win_prem_ticker,
            )
        except ImportError:
            print('Visdom not imported')
        return prem

    def log_data(self):
        pd.DataFrame(self.X).to_csv("./log/"+self.alt_name+"/X.csv")
        pd.DataFrame(self.Y_prem_pos).to_csv("./log/"+self.alt_name+"/Y_prem_pos.csv")
        pd.DataFrame(self.Y_prem_neg).to_csv("./log/"+self.alt_name+"/Y_prem_neg.csv")
        pd.DataFrame(self.Y_krx_altkrw_sell_price).to_csv("./log/"+self.alt_name+"/Y_krx_altkrw_sell_price.csv")
        pd.DataFrame(self.Y_krx_altkrw_buy_price).to_csv("./log/"+self.alt_name+"/Y_krx_altkrw_buy_price.csv")
        pd.DataFrame(self.Y_krx_btckrw_sell_price).to_csv("./log/"+self.alt_name+"/Y_krx_btckrw_sell_price.csv")
        pd.DataFrame(self.Y_krx_btckrw_buy_price).to_csv("./log/"+self.alt_name+"/Y_krx_btckrw_buy_price.csv")
        pd.DataFrame(self.Y_krx_sell_price).to_csv("./log/"+self.alt_name+"/Y_krx_sell_price.csv")
        pd.DataFrame(self.Y_krx_buy_price).to_csv("./log/"+self.alt_name+"/Y_krx_buy_price.csv")
        pd.DataFrame(self.Y_polo_sell_price).to_csv("./log/"+self.alt_name+"/Y_polo_sell_price.csv")
        pd.DataFrame(self.Y_polo_buy_price).to_csv("./log/"+self.alt_name+"/Y_polo_buy_price.csv")
        pd.DataFrame(self.Y_polo_btcusd_price).to_csv("./log/"+self.alt_name+"/Y_polo_btcusd_price.csv")
