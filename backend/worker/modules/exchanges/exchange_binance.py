import datetime
import requests
import json

RO_API_KEY_NAME = 'BINANCE_RO_API_KEY'
RO_SECRET_KEY_NAME = 'BINANCE_RO_SECRET_KEY'
DEFAULT_TARGET_ASSETS = 'BTC,USDT'
DEFAULT_INTERVAL = '1m'

WEBSOCKET_CONNECTION_STRING = 'wss://stream.binance.com:9443/ws'
HTTP_CONNECTION_STRING = 'https://api.binance.com'
PAIR_PATH = '/api/v3/exchangeInfo'


class Exchange:
    def __init__(self, target_assets=DEFAULT_TARGET_ASSETS, interval=DEFAULT_INTERVAL):
        self.target_assets = target_assets.split(',')
        self.interval = interval
        self.subscription_message = self.get_subscriptions_params()
        self.target_pairs = []
        self.update_trade_pairs()

    def get_subscriptions_params(self):
        self.update_trade_pairs()
        return {
            "method": "SUBSCRIBE",
            "params": ([(pair.lower()+"@kline_"+self.interval) for pair in self.target_pairs]),
            "id": 1
        }

    def update_trade_pairs(self):
        r = requests.get(HTTP_CONNECTION_STRING+PAIR_PATH)
        if r.status_code == 200:
            json_response = r.json()
            self.target_pairs = []
            for symbol in json_response['symbols']:
                if symbol['isSpotTradingAllowed'] and symbol['quoteAsset'] in self.target_assets:
                    self.target_pairs += [symbol['symbol']]
        else:
            print("Cant reach exchange to get Symbol")

    def map_fields(self, raw_message):
        return {
        "starttime": datetime.datetime.fromtimestamp(raw_message['k']['t'] / 1000.0),
        "endtime": datetime.datetime.fromtimestamp(raw_message['k']['T'] / 1000.0),
        "pair_name": raw_message['k']['s'],
        "interval": raw_message['k']['i'],
        "first_trade_id": raw_message['k']['f'],
        "last_trade_id": raw_message['k']['L'],
        "open": raw_message['k']['o'],
        "close": raw_message['k']['c'],
        "high": raw_message['k']['h'],
        "low": raw_message['k']['l'],
        "base_asset_volume": raw_message['k']['v'], # Klopt niet
        "quote_asset_volume": raw_message['k']['q'],
        "number_of_trades": raw_message['k']['n'],
        "is_kline_close": raw_message['k']['x']
        }

