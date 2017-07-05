from coinone.common import base_url, error_code
import base64
import simplejson as json
import hashlib
import hmac
import httplib2
import time
import logging

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Account:
    def __init__(self, token, key):
        self.token = token
        self.key = key
        self.default_payload = {"access_token": self.token}

    def info(self):
        return self._post('account/user_info')

    def balance(self):
        return self._post('account/balance')

    def daily_balance(self):
        return self._post('account/daily_balance')

    def deposit_address(self):
        return self._post('account/deposit_address')

    def virtual_account(self):
        return self._post('account/virtual_account')

    def orders(self, currency='btc'):
        payload = {**self.default_payload, 'currency': currency}
        return self._post('order/limit_orders', payload)['limitOrders']

    def complete_orders(self, currency='btc'):
        payload = {**self.default_payload, 'currency': currency}
        return self._post('order/complete_orders', payload)['completeOrders']

    def cancel(self, currency='btc',
               order_id=None, price=None, qty=None, is_ask=None, **kwargs):
        """
        cancel an order.
        If all params are empty, it will cancel all orders.
        """
        if all(param is None for param in (order_id, price, qty, is_ask)):
            payload = {**self.default_payload, 'currency': currency}
            url = 'order/cancel_all'
        elif 'type' in kwargs and 'orderId' in kwargs:
            payload = {**self.default_payload,
                       'price': price,
                       'qty': qty,
                       'is_ask': 1 if kwargs['type'] == 'ask' else 0,
                       'order_id': kwargs['orderId'],
                       'currency': currency}
            url = 'order/cancel'
        else:
            payload = {**self.default_payload,
                       'order_id': order_id,
                       'price': price,
                       'qty': qty,
                       'is_ask': is_ask,
                       'currency': currency}
            url = 'order/cancel'
        logger.debug('Cancel: %s' % payload)
        return self._post(url, payload)

    def buy(self, currency='btc', price=None, qty=None, **kwargs):
        """
        make a buy order.
        if quantity is not given, it will make a market price order.
        """
        if qty is None:
            payload = {**self.default_payload,
                       'price': price,
                       'currency': currency}
            url = 'order/market_buy'
        else:
            payload = {**self.default_payload,
                       'price': price,
                       'qty': qty,
                       'currency': currency}
            url = 'order/limit_buy'
        logger.debug('Buy: %s' % payload)
        return self._post(url, payload)

    def sell(self, currency='btc', qty=None, price=None, **kwargs):
        """
        make a sell order.
        if price is not given, it will make a market price order.
        """
        if price is None:
            payload = {**self.default_payload,
                       'qty': qty,
                       'currency': currency}
            url = 'order/market_sell'
        else:
            payload = {**self.default_payload,
                       'price': price,
                       'qty': qty,
                       'currency': currency}
            url = 'order/limit_sell'
        logger.debug('Sell: %s' % payload)
        return self._post(url, payload)

    def _post(self, url, payload=None):
        def encode_payload(payload):
            payload[u'nonce'] = int(time.time()*1000)
            ret = json.dumps(payload).encode()
            return base64.b64encode(ret)

        def get_signature(encoded_payload, secret_key):
            signature = hmac.new(
                secret_key.upper().encode(), encoded_payload, hashlib.sha512)
            return signature.hexdigest()

        def get_response(url, payload, key):
            encoded_payload = encode_payload(payload)
            headers = {
                'Content-type': 'application/json',
                'X-COINONE-PAYLOAD': encoded_payload,
                'X-COINONE-SIGNATURE': get_signature(encoded_payload, key)
            }
            http = httplib2.Http()
            response, content = http.request(
                url, 'POST', headers=headers, body=encoded_payload)
            return content

        if payload is None:
            payload = self.default_payload
        res = get_response(base_url+url, payload, self.key)
        res = json.loads(res)
        if res['result'] == 'error':
            err = res['errorCode']
            raise Exception(int(err), error_code[err])
        return res
