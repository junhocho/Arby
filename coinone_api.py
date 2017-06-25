#import urllib2
from urllib.request import urlopen
import json
import multiprocessing
from pprint import pprint


"""def work(url):
    response = urlopen(url)
    data = json.loads(response.read())

    return data
"""

class CoinOne():

    def __init__(self):
        #self.types = ['btc', 'eth', 'etc', 'xrp']
        self.types = ['eth']
        self.base_url = 'https://api.coinone.co.kr'

    def currency(self):
        url = self.base_url + '/currency'
        response = urlopen(url)
        data = json.loads(response.read())
        if data['result'] == 'success':
            #pprint(data)
            return data['currency']

        print("Fail to get currency")

    def orderbook(self):

        def get_max(data):
            ask_min = min([x['price'] for x in data['ask']])
            bid_max = max([x['price'] for x in data['bid']])

            return ask_min, bid_max

        #pool = multiprocessing.Pool(2)
        url = self.base_url + "/orderbook/?currency=%s"
        datas = {}
        try:
            #XXX: more types, fix it
            for idx in range(len(self.types)):
                response = urlopen(url % self.types[idx])
                data = json.loads(response.read())
                datas[data['currency']] = get_max(data)

            return datas
            #results = pool.map(work, [url % x for x in self.types])


        except Exception as e:
            print(e)
            exit(1)

