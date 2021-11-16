import asyncio
import json
import os
import time
import warnings
from datetime import datetime

import requests
from web3 import Web3

from models.Pair import Pair
from models.Token import Token
from modules.stores.StoreTimescaledb import StoreTimescaledb as Store

#source: https://paohuee.medium.com/interact-binance-smart-chain-using-python-4f8d745fe7b7

warnings.filterwarnings("ignore", message="divide by zero encountered in divide")

web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
print(web3.isConnected())

class FetchPairTicker:

    apiKey = ""

    PANCAKESWAP_FACTORY_ADDRESS = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
    pancakeswapFactoryAbi = ""
    BNB_ADDRESS = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c" # Hack
    STANDARD_ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'

    BSCSCAN_API = "https://api.bscscan.com/api"
    
    activePairs = {}

    def __init__(self, apikey):
        self.apiKey = apikey
        self.store = Store()
        self.store.connect()
        return None

    async def fetchPancakeSwapAbi(self):
        self.pancakeswapFactoryAbi = await self.getAbi(self.PANCAKESWAP_FACTORY_ADDRESS)
        
    async def getAbi(self, address):
        contract_address = web3.toChecksumAddress(address)
        apiCall = self.BSCSCAN_API+"?module=contract&action=getabi&address="+str(contract_address)
        apiCall += "&apikey="
        apiCall += self.apiKey
        r = requests.get(url = apiCall)
        response = r.json()
        if response['status'] != '0':
            return response["result"]
            

    def getPairDetails(self, contract, abi):
        contract_address = web3.toChecksumAddress(contract)
        contract = web3.eth.contract(address=contract_address, abi=abi)
        totalSupply = contract.functions.totalSupply().call()
        contractName = contract.functions.name().call()
        contractSymbol = contract.functions.symbol().call()
        # print("\nFor Contract:", contract_address)
        # print("\tTotal Supply:", totalSupply)
        # print("\tContract Name:", contractName)
        # print("\tContract Symbol:", contractSymbol)
        return [totalSupply , contractName, contractSymbol]

    # async def fetchPairUpdate(self):
        # address = "0x6897CBB72834A1586154EE6b68a114cc5311f2B6"
        # self.getPairDetails(address, await self.getAbi(address))
    
    async def getPairFromEvent(self, event):
        startTime = datetime.now()
        
        token0Address = event["args"]["token0"]
        [totalSupply , contractName, contractSymbol] = self.getPairDetails(token0Address, await self.getAbi(token0Address) or self.STANDARD_ABI)
        token0 = Token(
            tokenAddress = token0Address,
            name = contractName,
            symbol = contractSymbol,
            startTime = startTime,
            atBlockNr = event["blockNumber"],
            atBlockHash = event["blockHash"],
            transactionIndex = event["transactionIndex"],
            transactionHash = event["transactionHash"],
            totalSupply = totalSupply,
            active = True
        )
        
        token1Address = event["args"]["token1"]
        [totalSupply , contractName, contractSymbol] = self.getPairDetails(token1Address, await self.getAbi(token1Address) or self.STANDARD_ABI)
        token1 = Token(
            tokenAddress = token1Address,
            name = contractName,
            symbol = contractSymbol,
            startTime = startTime,
            atBlockNr = event["blockNumber"],
            atBlockHash = event["blockHash"],
            transactionIndex = event["transactionIndex"],
            transactionHash = event["transactionHash"],
            totalSupply = totalSupply,
            active = True
        )
        
        pair = Pair(
            token0 = token0,
            token1 = token1,
            address = event["args"]["pair"],
            startTime = startTime,
            atBlockNr = event["blockNumber"],
            atBlockHash = event["blockHash"],
            transactionIndex = event["transactionIndex"],
            transactionHash = event["transactionHash"],
        )
        return pair


    async def getActivePairList(self):        
        # TODO: delta logic
        self.activePairs = self.store.getActivePairs(idOnly=True)
    
    async def fetchPairTicks(self):
        
        await self.getActivePairList()
        print(self.activePairs)
        
        # contract = web3.eth.contract(address=self.PANCAKESWAP_FACTORY_ADDRESS, abi=self.pancakeswapFactoryAbi)
        # paircreated_Event = contract.events.PairCreated() # Modification


        # warnings.filterwarnings('ignore', '.*The event signature did not match the provided ABI.*', )
        # block_filter = web3.eth.filter({'fromBlock':'latest', 'address': self.PANCAKESWAP_FACTORY_ADDRESS})
        # # log_loop(block_filter, 2)
        
        # async def handle_event(event):
        #     receipt = web3.eth.waitForTransactionReceipt(event['transactionHash'])
        #     result = paircreated_Event.processReceipt(receipt) # Modification
            
        #     for resultItem in result:
        #         pair = await self.getPairFromEvent(resultItem)
        #         self.store.storePair(pair)
        #     # printDetails(result[0]['args'].token0, pair_abi)

        


        # async def periodic(event_filter):
        #     while True:
        #         for event in event_filter.get_new_entries():
        #             await handle_event(event)
        #         await asyncio.sleep(1)

        # # def stop():
        # #     task.cancel()
        # loop = asyncio.get_event_loop()
        # # loop.call_later(5, stop)
        # task = loop.create_task(periodic(block_filter))

        # await task

async def main():
    fetchPairTicker = FetchPairTicker(os.environ.get('APITOKEN'))
    await fetchPairTicker.fetchPancakeSwapAbi()
    await fetchPairTicker.fetchPairTicks()

if __name__ == "__main__":
    import time
    s = time.perf_counter()
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        pass
    
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
