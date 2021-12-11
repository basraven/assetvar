import asyncio
import json
import os
import time
import warnings
from datetime import datetime

import random 

import requests
from web3 import Web3
from web3.exceptions import ContractLogicError

import multiprocessing as mp

from panalyze.models.PairPrice import PairPrice
from panalyze.models.Token import Token
from panalyze.modules.stores.StoreTimescaledb import StoreTimescaledb as Store

# Source: https://paohuee.medium.com/interact-binance-smart-chain-using-python-4f8d745fe7b7
# Source: https://gist.github.com/Linch1/ede03999f483f2b1d5fcac9e8b312f2c

warnings.filterwarnings("ignore", message="divide by zero encountered in divide")
warnings.filterwarnings("ignore", message=".*INSUFFICIENT_LIQUIDIT.*")

web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
# print(web3.isConnected())

session = None

STANDARD_ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"TokentateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'

PANCAKESWAP_ROUTER_ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
PANCAKESWAP_FACTORY_ADDRESS = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
pancakeswapFactoryAbi = ""
pancakeswapRouterAbi = ""


def getCorrectedDecimals(number, decimals ):
    number = str(number)
    numberAbs = number.split('.')[0]
    
    numberDecimals = ''
    if len(number.split(".")) > 1:
        numberDecimals = number.split('.')[1]
    while( len(numberDecimals) < decimals ):
        numberDecimals += "0"
    
    return int(numberAbs + numberDecimals)

def set_global_session():
    global session
    if not session:
        session = requests.Session()
    
# @asyncio.coroutine
def fetchTick(contextObject):
    pair = contextObject['pair']
    targetTokenDecimals = contextObject['targetTokenDecimals']
    stableCoinPrices = contextObject['stableCoinPrices']
    currentTime = contextObject['currentTime']
    
    lastPrice = contextObject['lastPrice']
    activePairs = contextObject['activePairs']
    
    removeFromActivePairs = []

    # dt = "0x1749b7ff7eDD02a51f9D7075eC5875a106CF05B5"
    try:
        # if pair.address == dt:
        #     t1 = time.procefss_time()
            
        if pair.token0 in Token.STABLE_COINS.values():
            targetToken = pair.token1
            stableCoin = pair.token0
        elif pair.token1 in Token.STABLE_COINS.values():
            targetToken = pair.token0
            stableCoin = pair.token1
        else:
            # print("Not found a stable coin\n \t pair %s \n \t token0 %s \n \t token1 %s" % (pair.address, pair.token0, pair.token1))
            activePairs.remove(pair)
            removeFromActivePairs.append[{"reason" : 2, "pair" : pair}]
            # self.store.markUnactive(pair)
            return
        
        # print(pair.address)
        # return random.randint(0,100)
        # if pair.address == dt:
        #     tn1 = time.process_time()
        #     print("tn1: %s seconds"%(tn1 - t1))
        
        # TODO: Write to db instead of get at runtime
        if targetToken not in targetTokenDecimals:
            # print("Added decimals details to runtime cache for: " + targetToken)
            tokenRouter = web3.eth.contract( address=web3.toChecksumAddress(targetToken), abi=STANDARD_ABI )
            targetTokenDecimals[targetToken] = tokenRouter.functions.decimals().call()
            
        # Amount of tokens we want the price for is always 1
        tokensToSell = getCorrectedDecimals(1, targetTokenDecimals[targetToken])

        router = web3.eth.contract( abi=pancakeswapRouterAbi, address=web3.toChecksumAddress(PANCAKESWAP_ROUTER_ADDRESS) )
        
        # Using token0 and token1 here because the order is important
        amountOut = router.functions.getAmountsOut(int(tokensToSell), [web3.toChecksumAddress(pair.token0) , web3.toChecksumAddress(pair.token1)]).call()
        amountOut =  web3.fromWei(number=amountOut[1], unit='ether')
        
        if pair.address not in lastPrice:
            lastPrice[pair.address] = amountOut
        elif lastPrice[pair.address] == amountOut:
            # Lets only update the db is there is something to update it for
            return
        
        priceStableCoin = 0
        if stableCoin == Token.STABLE_COINS["USDT"]:
            priceUsdt = amountOut
        if stableCoin in Token.STABLE_COINS.values():
            stableCoinName = [k for k, v in Token.STABLE_COINS.items() if v == stableCoin][0]
            priceStableCoin = amountOut
            priceUsdt = (priceStableCoin * stableCoinPrices[stableCoinName])
            
                        
        # print("BNB Price: " + str(priceStableCoin) + " in USDT: " + str(priceUsdt) )
        
        return {
                "lastPrice" : lastPrice,
                "removeFromActivePairs" : removeFromActivePairs,
                "pairPrice" : PairPrice(currentTime=currentTime, pairAddress=pair.address, priceStableCoin=priceStableCoin, priceUsdt=priceUsdt, targetToken=targetToken, stableCoin=stableCoin)  
            }
        
         
        
    except Exception as err:
        if "PancakeLibrary: INSUFFICIENT_LIQUIDITY" in str(err):
            pass
        else:
            timeString = datetime.now().strftime("%H:%M:%S") 
            print(f"{timeString}: Exception occured: {err}")
        # pass


class FetchPairTicker:

    apiKey = ""
    stableCoinPrices = dict()
    targetTokenDecimals = dict()
    lastPrice = dict()    
    
    BSCSCAN_API = "https://api.bscscan.com/api"
    
    activePairs = {}

    def __init__(self, apikey):
        self.apiKey = apikey
        self.store = Store()
        self.store.connect()
        return None

    def fetchPancakeSwapAbi(self):
        global pancakeswapFactoryAbi, pancakeswapRouterAbi
        pancakeswapFactoryAbi = self.getAbi(PANCAKESWAP_FACTORY_ADDRESS)
        pancakeswapRouterAbi = self.getAbi(PANCAKESWAP_ROUTER_ADDRESS)
        
    def getAbi(self, address):
        contract_address = web3.toChecksumAddress(address)
        apiCall = self.BSCSCAN_API+"?module=contract&action=getabi&address="+str(contract_address)
        apiCall += "&apikey="
        apiCall += self.apiKey
        r = requests.get(url = apiCall)
        response = r.json()
        if response['status'] != '0':
            return response["result"]
            

    def updateStableCoinsToUSDTPrice(self):
        for stableCoinName in Token.STABLE_COINS:
            try:
                if stableCoinName == "USDT":
                    self.stableCoinPrices[stableCoinName] = 1
                    continue
                stableCoinToSell = web3.toWei("1", "ether")        
                router = web3.eth.contract( abi=pancakeswapRouterAbi, address=web3.toChecksumAddress(PANCAKESWAP_ROUTER_ADDRESS) )
                amountOut = router.functions.getAmountsOut(stableCoinToSell, [web3.toChecksumAddress(Token.STABLE_COINS[stableCoinName]) , web3.toChecksumAddress(Token.STABLE_COINS["USDT"])]).call()
                self.stableCoinPrices[stableCoinName] =  web3.fromWei(number=amountOut[1], unit='ether')
                print("\t%s price: %s" % (stableCoinName, str(self.stableCoinPrices[stableCoinName]) ))
            except Exception as err:
                timeString = datetime.now().strftime("%H:%M:%S") 
                print(f"{timeString}: Exception occured while updating {stableCoinName} price: {err}")
                pass
        

    def getActivePairList(self):        
        # TODO: delta logic
        try:
            self.activePairs = self.store.getActivePairs(idsOnly=True) #[-2:-1] # 0xd1fe404c759bedddbfb5dcdc1ccefa401a2cd5ea
        except Exception as err:
            timeString = datetime.now().strftime("%H:%M:%S") 
            print(f"{timeString}: Exception occured while getting active pairs: {err}")
            pass
        
    def getContextObject(self, pair):
        return {
            "pair": pair,
            "targetTokenDecimals": self.targetTokenDecimals,
            "stableCoinPrices" : self.stableCoinPrices,
            "currentTime" : self.currentTime,
            "activePairs" : self.activePairs,
            "lastPrice" : self.lastPrice
        }
    
    def fetchPairTicks(self):    

        while True:
            try:            
                self.currentTime = datetime.now() 
                print("Fetching pairs ticks: %s"%self.currentTime)
                self.getActivePairList()
                self.updateStableCoinsToUSDTPrice()
                start_time = time.time()
                
                with mp.Pool(initializer=set_global_session, processes=(mp.cpu_count() * 2)) as pool:
                    fetchTickReturnList = pool.map(fetchTick, [self.getContextObject(pair) for pair in self.activePairs] )
                # asyncio.get_event_loop().run_until_complete(asyncio.gather(*(fetchTick(self.getContextObject(pair)) for pair in self.activePairs) ))
                
                pairPriceList = []
                for item in fetchTickReturnList:
                    if item:
                        if "pairPrice" in item:
                            pairPriceList.append(item["pairPrice"])
                        if "lastPrice" in item:
                            for lastPriceUpdateKey in item["lastPrice"]:
                                if item["lastPrice"][lastPriceUpdateKey]:
                                    self.lastPrice[lastPriceUpdateKey] = item["lastPrice"][lastPriceUpdateKey]
                        if "removeFromActivePairs" in item:
                            if len(item["removeFromActivePairs"]) > 0:
                                for removeObject in item["removeFromActivePairs"]:
                                    self.activePairs.remove(removeObject["pair"])
                                    self.store.filterTokenActive(Token.getTargetTokenFromPair(pair=removeObject["pair"]), removeObject["reason"])
                                    
                
                self.store.storePairPriceList(pairPriceList)              
                
                elapsed_time =  (time.time() - start_time)
                print("Fetching ticks took: %s seconds"%elapsed_time)
                print("\n---")
                if elapsed_time < 5:
                    print("Sleeping...")
                    time.sleep(10)
            except Exception as err:
                timeString = datetime.now().strftime("%H:%M:%S") 
                print(f"{timeString}: Exception occured: {err}")
            finally:
                pool.close()
                
            

def main():
    fetchPairTicker = FetchPairTicker(os.environ.get('APITOKEN'))
    fetchPairTicker.fetchPancakeSwapAbi()
    fetchPairTicker.fetchPairTicks()

if __name__ == "__main__":
    import time
    s = time.perf_counter()
    main()   
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
