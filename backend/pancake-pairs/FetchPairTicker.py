import asyncio
import json
import os
import time
import warnings
from datetime import datetime

import requests
from web3 import Web3
from web3.exceptions import ContractLogicError
from models.PairPrice import PairPrice
from models.Token import Token
from modules.stores.StoreTimescaledb import StoreTimescaledb as Store

# Source: https://paohuee.medium.com/interact-binance-smart-chain-using-python-4f8d745fe7b7
# Source: https://gist.github.com/Linch1/ede03999f483f2b1d5fcac9e8b312f2c

warnings.filterwarnings("ignore", message="divide by zero encountered in divide")
warnings.filterwarnings("ignore", message=".*INSUFFICIENT_LIQUIDIT.*")

web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
print(web3.isConnected())

class FetchPairTicker:

    apiKey = ""
    stableCoinPrices = dict()
    targetTokenDecimals = dict()
    lastPrice = dict()

    PANCAKESWAP_FACTORY_ADDRESS = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
    PANCAKESWAP_ROUTER_ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

    
    STANDARD_ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"TokentateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'

    BSCSCAN_API = "https://api.bscscan.com/api"
    
    activePairs = {}

    def __init__(self, apikey):
        self.apiKey = apikey
        self.store = Store()
        self.store.connect()
        return None

    async def fetchPancakeSwapAbi(self):
        self.pancakeswapFactoryAbi = await self.getAbi(self.PANCAKESWAP_FACTORY_ADDRESS)
        self.pancakeswapRouterAbi = await self.getAbi(self.PANCAKESWAP_ROUTER_ADDRESS)
        
    async def getAbi(self, address):
        contract_address = web3.toChecksumAddress(address)
        apiCall = self.BSCSCAN_API+"?module=contract&action=getabi&address="+str(contract_address)
        apiCall += "&apikey="
        apiCall += self.apiKey
        r = requests.get(url = apiCall)
        response = r.json()
        if response['status'] != '0':
            return response["result"]
            

    def getCorrectedDecimals(self, number, decimals ):
        number = str(number)
        numberAbs = number.split('.')[0]
        
        numberDecimals = ''
        if len(number.split(".")) > 1:
            numberDecimals = number.split('.')[1]
        while( len(numberDecimals) < decimals ):
            numberDecimals += "0"
        
        return int(numberAbs + numberDecimals)


    async def updateStableCoinsToUSDTPrice(self):
        for stableCoinName in Token.STABLE_COINS:
            try:
                if stableCoinName == "USDT":
                    self.stableCoinPrices[stableCoinName] = 1
                    continue
                stableCoinToSell = web3.toWei("1", "ether")        
                router = web3.eth.contract( abi=self.pancakeswapRouterAbi, address=web3.toChecksumAddress(self.PANCAKESWAP_ROUTER_ADDRESS) )
                amountOut = router.functions.getAmountsOut(stableCoinToSell, [web3.toChecksumAddress(Token.STABLE_COINS[stableCoinName]) , web3.toChecksumAddress(Token.STABLE_COINS["USDT"])]).call()
                self.stableCoinPrices[stableCoinName] =  web3.fromWei(number=amountOut[1], unit='ether')
                print("%s price: %s" % (stableCoinName, str(self.stableCoinPrices[stableCoinName]) ))
            except Exception as err:
                timeString = datetime.now().strftime("%H:%M:%S") 
                print(f"{timeString}: Exception occured while updating {stableCoinName} price: {err}")
                pass
        

    async def getActivePairList(self):        
        # TODO: delta logic
        try:
            self.activePairs = self.store.getActivePairs(idsOnly=True) #[-2:-1] # 0xd1fe404c759bedddbfb5dcdc1ccefa401a2cd5ea
        except Exception as err:
            timeString = datetime.now().strftime("%H:%M:%S") 
            print(f"{timeString}: Exception occured while getting active pairs: {err}")
            pass
        
    
    async def fetchPairTicks(self):
        
        async def fetchTick(pair, currentTime):
            try:
                
                if pair.token0 in Token.STABLE_COINS.values():
                    targetToken = pair.token1
                    stableCoin = pair.token0
                elif pair.token1 in Token.STABLE_COINS.values():
                    targetToken = pair.token0
                    stableCoin = pair.token1
                else:
                    # print("Not found a stable coin\n \t pair %s \n \t token0 %s \n \t token1 %s" % (pair.address, pair.token0, pair.token1))
                    self.activePairs.remove(pair)
                    self.store.markUnactive(pair)
                    return
                
                # TODO: Write to db instead of get at runtime
                if targetToken not in self.targetTokenDecimals:
                    # print("Added decimals details to runtime cache for: " + targetToken)
                    tokenRouter = web3.eth.contract( address=web3.toChecksumAddress(targetToken), abi=self.STANDARD_ABI )
                    self.targetTokenDecimals[targetToken] = tokenRouter.functions.decimals().call()
                
                # Amount of tokens we want the price for is always 1
                tokensToSell = self.getCorrectedDecimals(1, self.targetTokenDecimals[targetToken])

                router = web3.eth.contract( abi=self.pancakeswapRouterAbi, address=web3.toChecksumAddress(self.PANCAKESWAP_ROUTER_ADDRESS) )
                # Using token0 and token1 here because the order is important
                amountOut = router.functions.getAmountsOut(int(tokensToSell), [web3.toChecksumAddress(pair.token0) , web3.toChecksumAddress(pair.token1)]).call()
                amountOut =  web3.fromWei(number=amountOut[1], unit='ether')
                
                if pair.address not in self.lastPrice:
                    self.lastPrice[pair.address] = amountOut
                elif self.lastPrice[pair.address] == amountOut:
                    # Lets only update the db is there is something to update it for
                    return
                
                priceStableCoin = 0
                if stableCoin == Token.STABLE_COINS["USDT"]:
                    priceUsdt = amountOut
                if stableCoin in Token.STABLE_COINS.values():
                    stableCoinName = [k for k, v in Token.STABLE_COINS.items() if v == stableCoin][0]
                    priceStableCoin = amountOut
                    priceUsdt = (priceStableCoin * self.stableCoinPrices[stableCoinName])
                    
                                
                # print("BNB Price: " + str(priceStablecoin) + " in USDT: " + str(priceUsdt) )
                
                return PairPrice(currentTime=currentTime, pairAddress=pair.address, priceStableCoin=priceStableCoin, priceUsdt=priceUsdt, targetToken=targetToken, stableCoin=stableCoin)
                
            except Exception as err:
                if "PancakeLibrary: INSUFFICIENT_LIQUIDITY" in str(err):
                    pass
                else:
                    timeString = datetime.now().strftime("%H:%M:%S") 
                    print(f"{timeString}: Exception occured: {err}")
                # pass


        while True:
            await self.getActivePairList()
            await self.updateStableCoinsToUSDTPrice()
            currentTime = datetime.now()
            self.store.storePairPriceList( await asyncio.gather(*[fetchTick(pair=pair, currentTime=currentTime) for pair in self.activePairs]) )
            print("\n---")
            await asyncio.sleep(30)
            

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
