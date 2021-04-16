#!/usr/bin/env python
import asyncio
import websockets
import json
import os
import logging
import time
import pandas as pd

# Sources used
# https://gist.github.com/stefanotorresi/bfb9716f73f172ac4439436456a96d6f


# Custom libs
from modules.exchanges import exchange_binance as exchange
from modules.stores import store_timescaledb as store
from modules.techanalysis import techanalysis_all

TARGET_ASSETS = os.environ.get("TARGET_ASSETS") or "USDT" # Comma separated "USDT,BTC"
INTERVAL = os.environ.get('INTERVAL') or "1m"
REPORT_COUNT = int(os.environ.get('REPORT_COUNT')) if os.environ.get('REPORT_COUNT') else 100
HISTORY_COUNT = int(os.environ.get('HISTORY_COUNT')) if os.environ.get('HISTORY_COUNT') else 100


def _create_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("get_ws")
    logger.setLevel(logging.INFO)
    return logger

class Get_socket_binance:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.logger = _create_logger()
        self.exchange = exchange.Exchange(TARGET_ASSETS, INTERVAL)
        self.batch_size = len(self.exchange.target_pairs)
        self.store = store.Store()
        self.store.connect()
        self.processed_transactions = 0
        self.techanalyzer = techanalysis_all.Techanalyzer()
        
    def add_to_history(self, candle_value):
        if not hasattr(self, 'history'):
            self.history = pd.DataFrame([candle_value])
            return
        while len(self.history.index) > (HISTORY_COUNT * self.batch_size):
            self.history = self.history[:-1] # Remove last row -1
        self.history = self.history.append(pd.DataFrame([candle_value]))


    async def wait_forever(self, websocket):
        forever_wait = True
        batch_counter = 0
        with self.store.connection:
            while forever_wait: 
                raw_message = json.loads(await websocket.recv())
                self.processed_transactions += 1
                if self.processed_transactions % REPORT_COUNT == 0:
                    self.logger.info("Processed %i messages" % self.processed_transactions)
                # self.logger.info(raw_message)

                candle_value = self.exchange.map_fields(raw_message)
                if candle_value["is_kline_close"]:
                    batch_counter += 1
                    self.add_to_history(candle_value)
                    # self.logger.info(candle_value)
                    analyzed_candle = self.techanalyzer.analyze(candle_value, self.history)
                    if batch_counter == self.batch_size:  # Reset counter
                        self.store.save_candle(candle_value, True)
                        self.store.save_analysis(analyzed_candle, True)
                        batch_counter = 0
                    else:
                        self.store.save_candle(candle_value, False)
                        self.store.save_analysis(analyzed_candle, False)
        cur.close()


    async def ws_connect(self):
        async with websockets.connect(exchange.WEBSOCKET_CONNECTION_STRING) as websocket:

            logger = _create_logger()
            subscription_object = json.dumps(self.exchange.subscription_message)

            
            await websocket.send(subscription_object)
            confirmation = json.loads(await websocket.recv())
            
            logger.info(confirmation)
            if confirmation['result'] != None:
                logger.warn("Incorrect result!")
                return

            await self.wait_forever(websocket)
            
            
 
    def listen(self):
        self.loop.run_until_complete(self.ws_connect())



def main():
    get_socket_binance = Get_socket_binance()
    get_socket_binance.listen()


if __name__ == "__main__":
    main()



