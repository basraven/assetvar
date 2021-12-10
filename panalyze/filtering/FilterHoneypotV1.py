
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

web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
# print(web3.isConnected())

session = None

STANDARD_ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"TokentateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'

PANCAKESWAP_ROUTER_ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
PANCAKESWAP_FACTORY_ADDRESS = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
pancakeswapFactoryAbi = ""
pancakeswapRouterAbi = ""


minAge = os.environ.get('MINAGE') if os.environ.get('MINAGE') else '6 hours' # postgress interval value
maxTax = os.environ.get('MAXTAX') if os.environ.get('MAXTAX') else 50
maxGas = os.environ.get('MAXGAS') if os.environ.get('MAXGAS') else 1500000
sleepTime = os.environ.get('SLEEPTIME') if os.environ.get('SLEEPTIME') else 2
queryLimit = os.environ.get('QUERYLIMIT') if os.environ.get('QUERYLIMIT') else None


def set_global_session():
    global session
    if not session:
        session = requests.Session()
    
def filterPairOnHoneypot(contextObject):
    pair = contextObject['pair']
    currentTime = contextObject['currentTime']
    # targetTokenDecimals = contextObject['targetTokenDecimals']
    # stableCoinPrices = contextObject['stableCoinPrices']
    
    targetToken = Token.getTargetTokenFromPair(pair=pair)
    if targetToken == False or (pair.token0 != Token.STABLE_COINS["BNB"] and pair.token1 != Token.STABLE_COINS["BNB"]) :
        return
    
    # targetContract = web3.eth.contract( address=web3.toChecksumAddress(targetToken), abi=STANDARD_ABI )

    callData = "0xd66383cb000000000000000000000000" + targetToken.tokenAddress[2:]
    val = 100000000000000000 # FIXME: should be something different

    # Using this to reduce pressure on http endpoint, this filter can be slow, that's fine (for now)
    time.sleep(sleepTime)
    

    # TODO: Use await from create function
    try:
        callResponse = web3.eth.call({
            "to": web3.toChecksumAddress('0x2bf75fd2fab5fc635a4c6073864c708dfc8396fc'), # for BNB
            # "to": web3.toChecksumAddress('0x5bf62ec82af715ca7aa365634fab0e8fd7bf92c7'), # for BUSD
            "from": web3.toChecksumAddress('0x8894e0a0c962cb723c1976a4421c95949be2d4e3'),
            "value": val,
            "gas": 45000000,
            "data": callData,
        })
        
        
        decoded = web3.codec.decode_abi(['uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256'], callResponse)
        buyExpectedOut = decoded[0]
        buyActualOut = decoded[1]
        sellExpectedOut = decoded[2]
        sellActualOut = decoded[3]
        buyGasUsed = decoded[4]
        sellGasUsed = decoded[5]
        buyTax = round((buyExpectedOut - buyActualOut) / buyExpectedOut * 100 * 10) / 10
        sellTax = round((sellExpectedOut - sellActualOut) / sellExpectedOut * 100 * 10) / 10
        return {
            "targetToken" : targetToken,
            "buyTax" : buyTax,
            "sellTax" : sellTax,
            "buyGasUsed" : buyGasUsed,
            "sellGasUsed" : sellGasUsed
        }
    except ContractLogicError as err:
        if "TRANSFER_FROM_FAILED" in str(err):
            # print("HONEYPOT FOUND")
            return {
                "targetToken" : targetToken,
                "exception" : "TRANSFER_FROM_FAILED"
            }
        if "INSUFFICIENT_LIQUIDITY" in str(err):
            return {
                "targetToken" : targetToken,
                "exception" : "INSUFFICIENT_LIQUIDITY"
            }
        if "TRANSFER_FAILED" in str(err):
            return {
                "targetToken" : targetToken,
                "exception" : "TRANSFER_FAILED"
            }
        if "execution reverted" in str(err):
            return {
                "targetToken" : targetToken,
                "exception" : "execution reverted"
            }
        else: 
            print(str(err))        

class FilterHoneypotV1:

    apiKey = ""   
    BSCSCAN_API = "https://api.bscscan.com/api"
    
    activeMinAgedPairs = {}

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
            
    def getActiveMinAgedPairList(self, minAge):        
        try:
            self.activeMinAgedPairs = self.store.getActivePairsMinAge(minAge, idsOnly=True, limit=queryLimit)
        except Exception as err:
            timeString = datetime.now().strftime("%H:%M:%S") 
            print(f"{timeString}: Exception occured while getting active tokens: {err}")
            pass
        
    def getContextObject(self, pair):
        return {
            "pair": pair,
            "currentTime" : self.currentTime,
        }
    
    def handleTokenDetail(self, tokenDetail):
        if "exception" in tokenDetail:
            if tokenDetail["exception"] == "INSUFFICIENT_LIQUIDITY":
                self.store.filterTokenHoneypotv1(token=tokenDetail["targetToken"], reason=502)
            if tokenDetail["exception"] == "TRANSFER_FROM_FAILED":
                self.store.filterTokenHoneypotv1(token=tokenDetail["targetToken"], reason=503)
            if tokenDetail["exception"] == "TRANSFER_FAILED":
                self.store.filterTokenHoneypotv1(token=tokenDetail["targetToken"], reason=102, toFilter=False)
            if tokenDetail["exception"] == "execution reverted":
                self.store.filterTokenHoneypotv1(token=tokenDetail["targetToken"], reason=104, toFilter=False)
        else:
            # Check if new filters are needed
            if(tokenDetail["buyTax"] + tokenDetail["sellTax"] > maxTax ):
                self.store.filterTokenHoneypotv1(token=tokenDetail["targetToken"], reason=504)
            if(tokenDetail["sellGasUsed"] > maxGas ):
                self.store.filterTokenHoneypotv1(token=tokenDetail["targetToken"], reason=505)
            if(tokenDetail["buyTax"] + tokenDetail["sellTax"] == 0.0 ):
                self.store.filterTokenHoneypotv1(token=tokenDetail["targetToken"], reason=103, reasonDetails="Tax is 0.0", toFilter=False)
        
            # Store generic outcome
            self.store.updateTokenTax(token=tokenDetail["targetToken"], buyTax=tokenDetail["buyTax"], selTax=tokenDetail["sellTax"])
            self.store.updateTokenGasSellUsed(token=tokenDetail["targetToken"], buyGasUsed=tokenDetail["buyGasUsed"], sellGasUsed=tokenDetail["sellGasUsed"])
                
    
    def filterForHoneyPots(self):
        
        while True:
            try:            
                self.currentTime = datetime.now()
                print("Filtering on Honeypot V1: %s"%self.currentTime)
                start_time = time.time()
                self.getActiveMinAgedPairList(minAge)
                
                
                # toCheckTokenAddresses = [
                #     # "0xe91a8d2c584ca93c7405f15c22cdfe53c29896e3",     # BNB: DEXT, no honeypot
                #     # "0xab43c532cd3293e26898fd5c03f0507c1f915f0b" ,    # BNB: ADANX, no honeypot but with taxes
                #     "0x8076c74c5e3f5852037f31ff0093eeb8c8add8d3" ,    # BNB: Safemoon, no honeypot but with taxes
                #     # "0x2014a3d523f1ac53f89590e987e7bd611424d5b8",     # BNB: XIDR, honeypot,
                #     # "0xc2931310a338a227bfb73b3132a90f107e7c5276",     # BNB: wrong address, 
                #     # "0xfd9faca15558eb243ac0012cf7acfbf480574668",     # BUSD: MVR, no honeypot, but low transactions 
                # ]
                
                # with mp.Pool(initializer=set_global_session, processes=(mp.cpu_count() * 2)) as pool:
                # with mp.Pool(initializer=set_global_session, processes=1) as pool:
                #     tokenDetails = pool.map(filterPairOnHoneypot, [self.getContextObject(pair) for pair in self.activeMinAgedPairs][10] )
                
                # TODO: one by one works for now...
                for pair in self.activeMinAgedPairs:
                    tokenDetail = filterPairOnHoneypot(self.getContextObject(pair))
                    if tokenDetail != None:
                        self.handleTokenDetail(tokenDetail)
                        
                        
                
                elapsed_time =  (time.time() - start_time)
                print("Fetching ticks took: %s seconds"%elapsed_time)
                print("\n---")
                if elapsed_time < 5:
                    print("Sleeping...")
                    time.sleep(10)
            except Exception as err:
                timeString = datetime.now().strftime("%H:%M:%S") 
                print(f"{timeString}: Exception occured: {err}")
            # finally:
            #     pool.close()
                
            

def main():
    filterHoneypotV1 = FilterHoneypotV1(os.environ.get('APITOKEN'))
    filterHoneypotV1.fetchPancakeSwapAbi()
    filterHoneypotV1.filterForHoneyPots()

if __name__ == "__main__":
    s = time.perf_counter()
    main()   
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
