import datetime

RO_API_KEY_NAME = 'BINANCE_RO_API_KEY'
RO_SECRET_KEY_NAME = 'BINANCE_RO_SECRET_KEY'

WEBSOCKET_CONNECTION_STRING = 'wss://stream.binance.com:9443/ws'


SUBSCRIPTION_PARAMS = [
    "btcusdt@kline_1m"
]

SUBSCRIPTION_MESSAGE = {
    "method": "SUBSCRIBE",
    "params": SUBSCRIPTION_PARAMS,
    "id": 1
}

def map_fields(raw_message):
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
      "base_asset_volume": raw_message['k']['v'],
      "quote_asset_volume": raw_message['k']['q'],
      "number_of_trades": raw_message['k']['n'],
      "is_kline_close": raw_message['k']['x']
    }

