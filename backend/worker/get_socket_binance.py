#!/usr/bin/env python
import asyncio
import websockets
import json
import os
import logging
import time

# Sources used
# https://gist.github.com/stefanotorresi/bfb9716f73f172ac4439436456a96d6f


# Custom libs
from modules.exchanges import exchange_binance as exchange
from modules.stores import store_timescaledb as store

def _create_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("get_ws")
    logger.setLevel(logging.INFO)
    return logger

class Get_socket_binance:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.logger = _create_logger()
        self.store = store.Store()
        self.store.connect()


    async def wait_forever(self, websocket):
        forever_wait = True
        with self.store.connection:
            while forever_wait: 
                raw_message = json.loads(await websocket.recv())
                candle_value = exchange.map_fields(raw_message)
                if candle_value["is_kline_close"]:
                    print(candle_value)
                    self.store.save_candle(candle_value)
        cur.close()


    async def ws_connect(self):
        async with websockets.connect(exchange.WEBSOCKET_CONNECTION_STRING) as websocket:

            logger = _create_logger()
            subscription_object = json.dumps(exchange.SUBSCRIPTION_MESSAGE)
            
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



