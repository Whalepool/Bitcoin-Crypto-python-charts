from __future__ import absolute_import
import requests
import json
import base64
import hmac
import hashlib
import time
from pprint import pprint
import sys

PROTOCOL = "https"
HOST = "api.bitfinex.com"
VERSION = "v2"


PATH_PUBLIC_TICKERS = 'tickers?symbols=%s'
PATH_PUBLIC_TICKER = 'ticker/%s'


PATH_TODAY = "today/%s"
PATH_STATS = "stats/%s"
PATH_LENDBOOK = "lendbook/%s"
PATH_ORDERBOOK = "book/%s"

# HTTP request timeout in seconds
TIMEOUT = 5.0

class AuthClient1:


    def __init__(self, key, secret):
        self.URL = "https://api.bitfinex.com/"
        self.KEY = key
        self.SECRET = secret
        pass

    @property
    def _nonce(self):
        """
        Returns a nonce
        Used in authentication
        """
        return str(time.time() * 1000000)

    def _sign_payload(self, payload):
        j = json.dumps(payload)
        data = base64.standard_b64encode(j.encode('utf8'))

        h = hmac.new(self.SECRET.encode('utf8'), data, hashlib.sha384)
        signature = h.hexdigest()
        return {
            "X-BFX-APIKEY": self.KEY,
            "X-BFX-SIGNATURE": signature,
            "X-BFX-PAYLOAD": data
        }


    def past_trades(self, symbol='btcusd', params={} ):
        """
        Fetch past trades
        :param timestamp:
        :param symbol:
        :return:
        """
        payload = {
            "request": "/v1/mytrades",
            "nonce": self._nonce,
            "symbol": symbol
        }
        if len(params.items()) > 0:
            for key, value in params.items():
                payload[key] = value


        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/v1/mytrades", headers=signed_payload, verify=True)


        if r.status_code == 200:
          return r.json()
        else:
          pprint(r.json())
          pprint(r.status_code)
          sys.exit()




class AuthClient2:
    """
    Authenticated client for trading through Bitfinex API
    """

    def __init__(self, key, secret):
        self.URL = "https://api.bitfinex.com/"
        self.KEY = key
        self.SECRET = secret
        pass

    @property
    def _nonce(self):
        """
        Returns a nonce
        Used in authentication
        """
        return str(int(round(time.time() * 1000)))

    def _headers(self, path, nonce, body):

        signature = "/api/" + path + nonce + body
        pprint("Signing: " + signature)
        h = hmac.new(self.SECRET.encode('utf8'), signature.encode('utf8'), hashlib.sha384)
        signature = h.hexdigest()

        return {
            "content-type": "application/json",
            "bfx-nonce": nonce,
            "bfx-apikey": self.KEY,
            "bfx-signature": signature,
        }

    def wallets(self):

        nonce = self._nonce
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/wallets"


        headers = self._headers(path, nonce, rawBody)

        r = requests.post(self.URL + path, headers=headers, data=rawBody, verify=True)

        if r.status_code == 200:
          return r.json()
        else:
          pprint(r.status_code)
          sys.exit()


    def active_orders(self):
        """
        Fetch active orders
        """
        nonce = self._nonce
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/orders"


        headers = self._headers(path, nonce, rawBody)

        r = requests.post(self.URL + path, headers=headers, data=rawBody, verify=True)

        if r.status_code == 200:
          return r.json()
        else:
          pprint(r.status_code)
          sys.exit()


    def place_order(self, amount, price, side, ord_type, symbol='btcusd', exchange='bitfinex'):
        """
        Submit a new order.
        :param amount:
        :param price:
        :param side:
        :param ord_type:
        :param symbol:
        :param exchange:
        :return:
        """
        payload = {

            "request": "/v1/order/new",
            "nonce": self._nonce,
            "symbol": symbol,
            "amount": amount,
            "price": price,
            "exchange": exchange,
            "side": side,
            "type": ord_type

        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/order/new", headers=signed_payload, verify=True)
        json_resp = r.json()

        try:
            json_resp['order_id']
        except:
            return json_resp['message']

        return json_resp

    def delete_order(self, order_id):
        """
        Cancel an order.
        :param order_id:
        :return:
        """
        payload = {
            "request": "/v1/order/cancel",
            "nonce": self._nonce,
            "order_id": order_id
        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/order/cancel", headers=signed_payload, verify=True)
        json_resp = r.json()

        try:
            json_resp['avg_excution_price']
        except:
            return json_resp['message']

        return json_resp

    def delete_all_orders(self):
        """
        Cancel all orders.

        :return:
        """
        payload = {
            "request": "/v1/order/cancel/all",
            "nonce": self._nonce,
        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/order/cancel/all", headers=signed_payload, verify=True)
        json_resp = r.json()
        return json_resp

    def status_order(self, order_id):
        """
        Get the status of an order. Is it active? Was it cancelled? To what extent has it been executed? etc.
        :param order_id:
        :return:
        """
        payload = {
            "request": "/v1/order/status",
            "nonce": self._nonce,
            "order_id": order_id
        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/order/status", headers=signed_payload, verify=True)
        json_resp = r.json()

        try:
            json_resp['avg_excution_price']
        except:
            return json_resp['message']

        return json_resp



    def active_positions(self):
        """
        Fetch active Positions
        """

        payload = {
            "request": "/v1/positions",
            "nonce": self._nonce
        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/positions", headers=signed_payload, verify=True)
        json_resp = r.json()
        return json_resp

    def claim_position(self, position_id):
        """
        Claim a position.
        :param position_id:
        :return:
        """
        payload = {
            "request": "/v1/position/claim",
            "nonce": self._nonce,
            "position_id": position_id
        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/position/claim", headers=signed_payload, verify=True)
        json_resp = r.json()

        return json_resp

    def past_trades(self, timestamp=0, symbol='btcusd'):
        """
        Fetch past trades
        :param timestamp:
        :param symbol:
        :return:
        """
        payload = {
            "request": "/v1/mytrades",
            "nonce": self._nonce,
            "symbol": symbol,
            "timestamp": timestamp
        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/mytrades", headers=signed_payload, verify=True)
        json_resp = r.json()

        return json_resp

    def place_offer(self, currency, amount, rate, period, direction):
        """

        :param currency:
        :param amount:
        :param rate:
        :param period:
        :param direction:
        :return:
        """
        payload = {
            "request": "/v1/offer/new",
            "nonce": self._nonce,
            "currency": currency,
            "amount": amount,
            "rate": rate,
            "period": period,
            "direction": direction
        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/offer/new", headers=signed_payload, verify=True)
        json_resp = r.json()

        return json_resp

    def cancel_offer(self, offer_id):
        """

        :param offer_id:
        :return:
        """
        payload = {
            "request": "/v1/offer/cancel",
            "nonce": self._nonce,
            "offer_id": offer_id
        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/offer/cancel", headers=signed_payload, verify=True)
        json_resp = r.json()

        return json_resp

    def status_offer(self, offer_id):
        """

        :param offer_id:
        :return:
        """
        payload = {
            "request": "/v1/offer/status",
            "nonce": self._nonce,
            "offer_id": offer_id
        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/offer/status", headers=signed_payload, verify=True)
        json_resp = r.json()

        return json_resp

    def active_offers(self):
        """
        Fetch active_offers
        :return:
        """
        payload = {
            "request": "/v1/offers",
            "nonce": self._nonce
        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/offers", headers=signed_payload, verify=True)
        json_resp = r.json()

        return json_resp

    def balances(self):
        """
        Fetch balances

        :return:
        """
        payload = {
            "request": "/v1/balances",
            "nonce": self._nonce
        }

        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/balances", headers=signed_payload, verify=True)
        json_resp = r.json()

        return json_resp

    def history(self, currency, since=0, until=9999999999, limit=500, wallet='exchange'):
        """
        View you balance ledger entries
        :param currency: currency to look for
        :param since: Optional. Return only the history after this timestamp.
        :param until: Optional. Return only the history before this timestamp.
        :param limit: Optional. Limit the number of entries to return. Default is 500.
        :param wallet: Optional. Return only entries that took place in this wallet. Accepted inputs are: “trading”,
        “exchange”, “deposit”.
        """
        payload = {
            "request": "/v1/history",
            "nonce": self._nonce,
            "currency": currency,
            "since": since,
            "until": until,
            "limit": limit,
            "wallet": wallet
        }
        signed_payload = self._sign_payload(payload)
        r = requests.post(self.URL + "/history", headers=signed_payload, verify=True)
        json_resp = r.json()

        return json_resp



class PublicClient:
    """
    Client for the bitfinex.com API.

    See https://www.bitfinex.com/pages/api for API documentation.
    """

    def tickers(self, symbols):
        """
        GET tickers
        """
        data = self._get(self.url_for(PATH_PUBLIC_TICKERS, (symbols)))
        return data 

    def ticker(self, symbol):
        """
        GET ticker
        """
        data = self._get(self.url_for(PATH_PUBLIC_TICKER, (symbol)))
        return data



    def _get(self, url):
        return requests.get(url, timeout=TIMEOUT).json()


    def _build_parameters(self, parameters):
        # sort the keys so we can test easily in Python 3.3 (dicts are not
        # ordered)
        keys = list(parameters.keys())
        keys.sort()

        return '&'.join(["%s=%s" % (k, parameters[k]) for k in keys])


    def server(self):
        return u"{0:s}://{1:s}/{2:s}".format(PROTOCOL, HOST, VERSION)


    def url_for(self, path, path_arg=None, parameters=None):

        # build the basic url
        url = "%s/%s" % (self.server(), path)

        # If there is a path_arh, interpolate it into the URL.
        # In this case the path that was provided will need to have string
        # interpolation characters in it, such as PATH_TICKER
        if path_arg:
            url = url % (path_arg)

        # Append any parameters to the URL.
        if parameters:
            url = "%s?%s" % (url, self._build_parameters(parameters))

        return url
