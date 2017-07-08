from yahoo_finance import Currency
import urllib.request
import time

## TODO Better init.
# ETC ETH XRP: BTC in krx. ALT in polo
class Arby:
    def __init__(self, polo_bot, krx_bot):
        r = 10
        self.polo_bot = polo_bot
        self.krx_bot = krx_bot
        self.alt_name = krx_bot.alt_name

        if self.alt_name == 'XRP':
            self.btc_polo = 0.01 *r # 3,360,000
            self.btc_krx = 0.19 *r# 3,360,000
            self.btc_depo_delayed = 0
            self.krw_krx = 200000*r
            self.alt_polo = 100*r #360
            self.alt_krx = 100*r
        elif self.alt_name == 'ETH':
            self.btc_polo = 0.01 *r # 3,360,000
            self.btc_krx = 0.19 *r# 3,360,000
            self.btc_depo_delayed = 0
            self.krw_krx = 200000*r
            self.alt_polo = 1*r
            self.alt_krx = 1*r # 400,000
        elif self.alt_name == 'ETC':
            self.btc_polo = 0.01 *r # 3,360,000
            self.btc_krx = 0.19 *r# 3,360,000
            self.btc_depo_delayed = 0
            self.krw_krx = 200000*r
            self.alt_polo = 15*r
            self.alt_krx = 15*r#26,000
        elif self.alt_name == 'LTC':
            self.polo_bot.btc_deposit(0.1)
            self.krx_bot.btc_deposit(0.1)
            self.polo_bot.alt_deposit(5)
            self.krx_bot.alt_deposit(5)
            self.krx_bot.krw_deposit(200000)
            # self.btc_polo = 0.1  # 3,360,000 #30
            # self.btc_krx = 0.1 # 3,360,000 #30
            # self.btc_depo_delayed = 0
            # self.krw_krx = 200000*r
            # self.alt_polo = 5 # 30
            # self.alt_krx = 5 # 55,800 # 30
        elif self.alt_name == 'DASH':
            self.polo_bot.btc_deposit(0.1)
            self.krx_bot.btc_deposit(0.1)
            self.polo_bot.alt_deposit(1.5)
            self.krx_bot.alt_deposit(1.5)
            self.krx_bot.krw_deposit(200000)
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
        self.time_tx = 10 #15*60


        self.btc_init = self.btc_sum()
        self.alt_init = self.alt_sum()
        self.asset_init = self.asset_in_btc()

        #self.btc_polo + self.btc_krx
        #self.alt_init = self.alt_polo + self.alt_krx
        self.eval_asset_init = self.asset_in_btc()
        self.btc_ratio = 1
        self.alt_ratio = 1

        self.prem_pos = 0
        self.prem_neg = 0
        self.prem_pos_failed = 0
        self.prem_neg_failed = 0
        self.reallo = 0


        # self.polo_btc_trade_amount = 0 # in BTC
        # self.krx_krw_trade_amount = 0 # in KRW



    def btc_sum(self):
        return self.polo_bot.btc_balance + self.krx_bot.btc_balance + self.polo_bot.btc_in_tx + self.krx_bot.btc_in_tx
    def alt_sum(self):
        return self.polo_bot.alt_balance + self.krx_bot.alt_balance + self.polo_bot.alt_in_tx + self.krx_bot.alt_in_tx
    def asset_in_btc(self):
        total_btc =  self.btc_sum() + self.polo_bot.eval_alt(self.alt_sum())
        return total_btc
    def asset_in_usd(self):
        return asset_in_btc() * self.polo_bot.btcusd()
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
        print('\tWorths BTC : {} \t ratio = {}'.format(btcsum, btcsum / self.asset_init))
        self.btc_ratio = self.btc_sum() / self.btc_init
        self.alt_ratio = self.alt_sum() / self.alt_init
        print('\tCoin ratio : BTC : {}\t {} : {}'.format(self.btc_ratio, self.alt_name, self.alt_ratio))
        print('\tArbitrage : +1 ({},{})\t -1 ({},{})\t Reallocate: {}\t'
                .format(self.prem_pos, self.prem_pos_failed, self.prem_neg, self.prem_neg_failed, self.reallo))
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
                # ALT : polo -> krx
                self.polo_alt_tx_info = self.polo_bot.transact_alt2krx(self.polo_bot.alt_balance)
            success = False

        try:
            self.polo_bot.btc2alt() # polo : BTC -> ALT
        except ValueError as e:
            print("\tPOLO : BTC -> {} : FAILED!!!!".
                    format(self.alt_name))
            if (self.krx_bot.btc_in_tx == 0):
                # BTC : krx -> polo
                self.krx_btc_tx_info = self.krx_bot.transact_btc2polo(self.krx_bot.btc_balance)
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
                # ALT : krx -> polo
                self.krx_alt_tx_info = self.krx_bot.transact_alt2polo(self.krx_bot.alt_balance) # SEND all ALT
            success = False

        try:
            self.krx_bot.btc2alt() # krx : BTC-> ALT
        except ValueError as e:
            print("\t{} : BTC -> {} : FAILED!!!!"
                    .format(self.krx_bot.exchange_name, self.alt_name))
            # BTC : polo -> krx
            if (self.polo_bot.btc_in_tx == 0):
                self.polo_btc_tx_info = self.polo_bot.transact_btc2krx(self.polo_bot.btc_balance) # SEND all BTC
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

    def check_transaction(self):
        if self.polo_alt_tx_info: # ALT : polo -> krx
            if time.time() - self.polo_alt_tx_info['time']  > self.time_tx:
                self.krx_bot.alt_deposit(self.polo_alt_tx_info['amount'])
                print("ALT : POLO -> {}".format(self.krx_bot.exchange_name))
                self.polo_alt_tx_info = None
                self.polo_bot.alt_in_tx = 0

        if self.polo_btc_tx_info:
            if time.time() - self.polo_btc_tx_info['time'] > self.time_tx:
                self.krx_bot.btc_deposit(self.polo_btc_tx_info['amount'])
                print("BTC : POLO -> {}".format(self.krx_bot.exchange_name))
                self.polo_btc_tx_info = None
                self.polo_bot.btc_in_tx = 0

        if self.krx_alt_tx_info:
            if time.time() - self.krx_alt_tx_info['time'] > self.time_tx:
                self.polo_bot.alt_deposit(self.krx_alt_tx_info['amount'])
                print("ALT : {} -> POLO".format(self.krx_bot.exchange_name))
                self.krx_alt_tx_info = None
                self.krx_bot.alt_in_tx = 0

        if self.krx_btc_tx_info:
            if time.time() - self.krx_btc_tx_info['time'] > self.time_tx:
                self.polo_bot.btc_deposit(self.krx_btc_tx_info['amount'])
                print("BTC : {} -> POLO".format(self.krx_bot.exchange_name))
                self.krx_btc_tx_info = None
                self.krx_bot.btc_in_tx = 0


    # def asset_reallocate(self): # Done instantly. Naive version.
    #     btc = self.btc_polo + self.btc_krx
    #     alt = self.alt_polo + self.alt_krx
    #     self.btc_polo = btc/2
    #     self.btc_krx = btc/2
    #     self.alt_polo = alt/2
    #     self.alt_krx = alt/2
    #     self.reallo += 1

    #     self.polo_with_amount = 0
    #     self.krx_with_amount = 0

    # def transact_btc_start(self, prem_alert):
    #     btc = self.btc_polo + self.btc_krx
    #     #if self.btc_polo > self.btc_krx:# polo -> krx
    #     if prem_alert == -1:
    #         btc_with =  self.btc_polo * 0.9 # withdraw 80%
    #         self.btc_depo_delayed = btc_with - commision_polo2krx

    #         self.btc_polo -= btc_with
    #         self.polo_with_amount += btc_with
    #         return 1 # polo -> krx
    #     #else:# krx -> polo
    #     elif prem_alert == +1:
    #         btc_with =  self.btc_krx * 0.9
    #         self.btc_depo_delayed = btc_with - commision_krx2polo

    #         self.btc_krx -= btc_with
    #         self.krx_with_amount += btc_with
    #         return -1 # krx -> polo

    # def transact_btc_done(self,tx_method):
    #     if tx_method == 1:# polo -> krx
    #         self.btc_krx += self.btc_depo_delayed
    #     elif tx_method == -1:# krx -> polo
    #         self.btc_polo += self.btc_depo_delayed
    #     self.btc_depo_delayed = 0

    def calculate_premium(self, count, threshold):
        # 	print('BITHUMB :  \tBUY: ', b_buy_price, '\tSELL: ', b_sell_price, '\t|')
        # 	print('POLO :   \tBUY: ', p_buy_price, '\tSELL: ', p_sell_price, '\t|')
        #print(pform.format(krx_name, krx_bot.buy_price, krx_bot.sell_price))
        #print(pform.format('POLONIEX', polo_bot.buy_price, polo_bot.sell_price))

        prem_pos_r = self.krx_bot.sell_price / (self.polo_bot.buy_price * (1 + self.polo_bot.fee_trd)) -1
        prem_neg_r = self.polo_bot.sell_price * (1 - self.polo_bot.fee_trd)/ self.krx_bot.buy_price -1

        print("\tPemium monitoring: POLO : BTC->{} | BITH : {}->BTC : {:5.2f}"
                .format(self.alt_name,
                    self.alt_name,
                    prem_pos_r * 100))
        print("\tPemium monitoring: POLO : {}->BTC | BITH : BTC->{} : {:5.2f}"
                .format(self.alt_name,
                    self.alt_name,
                    prem_neg_r * 100))
        #print()
        prem = 0

        #####  Premium compare ###### TODO Threshold : ratio? or delta?
        if(prem_pos_r > threshold):
            #### POLO : BTC -> Target   /    BITHUMB :  Taret -> BTC
            #print('#################### PREMIUM ALERT ####################\a')
            #print()
            print('\t{} :  {} -> BTC \t|\t POLO : BTC -> {}'
                    .format(self.krx_bot.exchange_name, self.alt_name, self.alt_name))
            print('\tPREM RATIO: ', prem_pos_r * 100, ' %')
            prem = 1
        if(prem_neg_r > threshold): # Each market threshold need comission
            #### POLO : Target -> BTC   /    BITHUMB :  BTC -> Target
            #print('#################### PREMIUM ALERT ####################\a')
            #print()
            print('\tPOLO : {} -> BTC \t|\t {} :  BTC -> {}'.format(self.alt_name,
                self.krx_bot.exchange_name, self.alt_name))
            print('\tPREM RATIO: ', prem_neg_r * 100, ' %')
            prem = -1
        #print()
        if count%100 == 0:
            usdkrw = Currency('USDKRW')
            curr = float(usdkrw.get_ask())
            btcusd = self.polo_bot.btcusd()
            print("\tBTC premeium KRW/USD : ",str((self.krx_bot.btckrw_buy_price / (curr * btcusd) )), 'with btcusd =',btcusd )
        return prem
