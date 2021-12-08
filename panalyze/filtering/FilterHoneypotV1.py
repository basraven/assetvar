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

# warnings.filterwarnings("ignore", message="divide by zero encountered in divide")
# warnings.filterwarnings("ignore", message=".*INSUFFICIENT_LIQUIDIT.*")

web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
# print(web3.isConnected())

session = None

STANDARD_ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"TokentateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'

PANCAKESWAP_ROUTER_ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
PANCAKESWAP_FACTORY_ADDRESS = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
pancakeswapFactoryAbi = ""
pancakeswapRouterAbi = ""


# def getCorrectedDecimals(number, decimals ):
#     number = str(number)
#     numberAbs = number.split('.')[0]
    
#     numberDecimals = ''
#     if len(number.split(".")) > 1:
#         numberDecimals = number.split('.')[1]
#     while( len(numberDecimals) < decimals ):
#         numberDecimals += "0"
    
#     return int(numberAbs + numberDecimals)

def set_global_session():
    global session
    if not session:
        session = requests.Session()
    
def filterPairOnHoneypot(contextObject):
    pair = contextObject['pair']
    currentTime = contextObject['currentTime']
    # targetTokenDecimals = contextObject['targetTokenDecimals']
    # stableCoinPrices = contextObject['stableCoinPrices']
    
    targetToken = ""
    targetTokenType = ""
    if pair.token0 == Token.STABLE_COINS["BNB"]:
        targetToken = pair.token1
        targetTokenType = "BNB"
    elif pair.token1 == Token.STABLE_COINS["BNB"]:
        targetToken = pair.token0
        targetTokenType = "BNB"
    else:
        # Currently only BNB is supported
        return
    
    targetContract = web3.eth.contract( address=web3.toChecksumAddress(targetToken), abi=STANDARD_ABI )

    callData = "0xd66383cb000000000000000000000000" + targetToken[2:]
    val = 100000000000000000 # FIXME: should be something different

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
    except ContractLogicError as err:
        if "TRANSFER_FROM_FAILED" in str(err):
            print("HONEYPOT FOUND")
            return
            
    
    decoded = web3.codec.decode_abi(['uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256'], callResponse)
    buyExpectedOut = decoded[0]
    buyActualOut = decoded[1]
    sellExpectedOut = decoded[2]
    sellActualOut = decoded[3]
    buyGasUsed = decoded[4]
    sellGasUsed = decoded[5]
    buy_tax = round((buyExpectedOut - buyActualOut) / buyExpectedOut * 100 * 10) / 10
    sell_tax = round((sellExpectedOut - sellActualOut) / sellExpectedOut * 100 * 10) / 10
    if(buy_tax + sell_tax > 80):
        print("Extremely high tax. Effectively a honeypot.")
    elif(buy_tax + sell_tax > 40):
        print("Really high tax.")

    if(sellGasUsed > 1500000):
        print("Selling costs a lot of gas.")
    
    print("Tax is: " + str(buy_tax + sell_tax))
    # let blacklisted = {
    #     '0xa914f69aef900beb60ae57679c5d4bc316a2536a': 'SPAMMING SCAM',
    #     '0x105e62565a31c269439b29371df4588bf169cef5': 'SCAM',
    #     '0xbbd1d56b4ccab9302aecc3d9b18c0c1799fe7525': 'Error: TRANSACTION_FROM_FAILED'
    # };
    # let unableToCheck = {
    #     '0x54810d2e8d3a551c8a87390c4c18bb739c5b2063': 'Coin does not utilise PancakeSwap',
    #     '0x7e946ee89a58691f0d21320ec8f684e29b890037': 'Honeypot cant check this token right now',
    #     '0xaA7836830a58bC9A90Ed0b412B31c2B84F1eaCBE': 'Honeypot cant check this token right now due to anti-bot measures',
    #     '0xc0834ee3f6589934dc92c63a893b4c4c0081de06': 'Due to anti-bot, Honeypot is not able to check at the moment.'
    # };

    # if(blacklisted[address.toLowerCase()] !== undefined) {
    #     let reason = blacklisted[address.toLowerCase()];
    #     document.getElementById('shitcoin').innerHTML = '<div style="max-width: 100%;" class="ui compact error message"><div class="header">Yup, honeypot. Run the fuck away.</div><p>Address: ' + addressToOutput + '</p><p id="token-info">'+tokenName + ' ('+tokenSymbol+')'+'</p><br>' + reason + '</div>';
    #     return;
    # }
    # if(unableToCheck[address.toLowerCase()] !== undefined) {
    #     let rreason = unableToCheck[address.toLowerCase()];
    #     document.getElementById('shitcoin').innerHTML = '<div style="max-width: 100%;" class="ui compact info message"><div class="header">Unable to check</div><p>The honeypot checker was unable to determine the result for the specified address.<br>'+rreason+'<br>Contact @ishoneypot on telegram for more.</p><p>Address: ' + addressToOutput + '</p><p id="token-info">'+tokenName + ' ('+tokenSymbol+')'+'</p><br>' + '' + '</div>';
    #     return;
    # }

    # let val = 100000000000000000;
    # if(bnbIN < val) {
    #     val = bnbIN - 1000;
    # }
    # web3.eth.call({
    #     to: '0x2bf75fd2fab5fc635a4c6073864c708dfc8396fc',
    #     from: '0x8894e0a0c962cb723c1976a4421c95949be2d4e3',
    #     value: val,
    #     gas: 45000000,
    #     data: callData,
    # })
    # .then((val) => {
    #     let warnings = [];
    #     let decoded = web3.eth.abi.decodeParameters(['uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256'], val);
    #     let buyExpectedOut = web3.utils.toBN(decoded[0]);
    #     let buyActualOut = web3.utils.toBN(decoded[1]);
    #     let sellExpectedOut = web3.utils.toBN(decoded[2]);
    #     let sellActualOut = web3.utils.toBN(decoded[3]);
    #     let buyGasUsed = web3.utils.toBN(decoded[4]);
    #     let sellGasUsed = web3.utils.toBN(decoded[5]);
    #     buy_tax = Math.round((buyExpectedOut - buyActualOut) / buyExpectedOut * 100 * 10) / 10;
    #     sell_tax = Math.round((sellExpectedOut - sellActualOut) / sellExpectedOut * 100 * 10) / 10;
    #     if(buy_tax + sell_tax > 80) {
    #         warnings.push("Extremely high tax. Effectively a honeypot.")
    #     }else if(buy_tax + sell_tax > 40) {
    #         warnings.push("Really high tax.");
    #     }
    #     if(sellGasUsed > 1500000) {
    #         warnings.push("Selling costs a lot of gas.");
    #     }
    #     console.log(buy_tax, sell_tax);
    #     let maxdiv = '';
    #     if(maxTXAmount != 0 || maxSell != 0) {
    #         let n = 'Max TX';
    #         let x = maxTXAmount;
    #         if(maxSell != 0) {
    #             n = 'Max Sell';
    #             x = maxSell;
    #         }
    #         let bnbWorth = '?'
    #         if(maxTxBNB != null) {
    #             bnbWorth = Math.round(maxTxBNB / 10**15) / 10**3;
    #         }
    #         let tokens = Math.round(x / 10**tokenDecimals);
    #         maxdiv = '<p>'+n+': ' + tokens + ' ' + tokenSymbol + ' (~'+bnbWorth+' BNB)</p>';
    #     }
    #     let warningmsg = '';
    #     let warningMsgExtra = '';
    #     let uiType = 'success';
    #     let warningsEncountered = false;
    #     if(warnings.length > 0) {
    #         warningsEncountered = true;
    #         uiType = 'warning';
    #         warningmsg = '<p><ul>WARNINGS';
    #         for(let i = 0; i < warnings.length; i++) {
    #             warningmsg += '<li>'+warnings[i]+'</li>';
    #         }
    #         warningmsg += '</ul></p>';
    #     }

    #     let gasdiv = '<p>Gas used for Buying: ' + numberWithCommas(buyGasUsed) + '<br>Gas used for Selling: ' + numberWithCommas(sellGasUsed) + '</p>';
    #     document.getElementById('shitcoin').innerHTML = '<div style="max-width: 100%;" class="ui compact '+uiType+' message"><div class="header">Does not seem like a honeypot.</div><p>This can always change! Do your own due diligence.</p>'+warningmsg+'<p>Address: ' + addressToOutput + '</p><p id="token-info">'+tokenName + ' ('+tokenSymbol+')'+'</p>'+maxdiv+gasdiv+'<p>Buy Tax: ' + buy_tax + '%<br>Sell Tax: ' + sell_tax + '%</p></div>';
    # })
    # .catch(err => {
    #     if(err == 'Error: Returned error: execution reverted') {
    #         document.getElementById('shitcoin').innerHTML = '<div style="max-width: 100%;" class="ui compact info message"><div class="header">Unable to check</div><p>The honeypot checker was unable to determine the result for the specified address.<br>Possible reasons for this:<ul><li>Invalid address</li><li>Token exists on a different chain</li><li>No liquidity paired wit…
    
    
    
    
    
    
    
#     lastPrice = contextObject['lastPrice']
#     activePairs = contextObject['activePairs']
    
#     removeFromActivePairs = []

#     # dt = "0x1749b7ff7eDD02a51f9D7075eC5875a106CF05B5"
#     try:
#         # if pair.address == dt:
#         #     t1 = time.procefss_time()
            
#         if pair.token0 in Token.STABLE_COINS.values():
#             targetToken = pair.token1
#             stableCoin = pair.token0
#         elif pair.token1 in Token.STABLE_COINS.values():
#             targetToken = pair.token0
#             stableCoin = pair.token1
#         else:
#             # print("Not found a stable coin\n \t pair %s \n \t token0 %s \n \t token1 %s" % (pair.address, pair.token0, pair.token1))
#             activePairs.remove(pair)
#             removeFromActivePairs.append[pair]
#             # self.store.markUnactive(pair)
#             return
        
#         # print(pair.address)
#         # return random.randint(0,100)
#         # if pair.address == dt:
#         #     tn1 = time.process_time()
#         #     print("tn1: %s seconds"%(tn1 - t1))
        
#         # TODO: Write to db instead of get at runtime
#         if targetToken not in targetTokenDecimals:
#             # print("Added decimals details to runtime cache for: " + targetToken)
#             tokenRouter = web3.eth.contract( address=web3.toChecksumAddress(targetToken), abi=STANDARD_ABI )
#             targetTokenDecimals[targetToken] = tokenRouter.functions.decimals().call()
            
#         # Amount of tokens we want the price for is always 1
#         tokensToSell = getCorrectedDecimals(1, targetTokenDecimals[targetToken])

#         router = web3.eth.contract( abi=pancakeswapRouterAbi, address=web3.toChecksumAddress(PANCAKESWAP_ROUTER_ADDRESS) )
        
#         # Using token0 and token1 here because the order is important
#         amountOut = router.functions.getAmountsOut(int(tokensToSell), [web3.toChecksumAddress(pair.token0) , web3.toChecksumAddress(pair.token1)]).call()
#         amountOut =  web3.fromWei(number=amountOut[1], unit='ether')
        
#         if pair.address not in lastPrice:
#             lastPrice[pair.address] = amountOut
#         elif lastPrice[pair.address] == amountOut:
#             # Lets only update the db is there is something to update it for
#             return
        
#         priceStableCoin = 0
#         if stableCoin == Token.STABLE_COINS["USDT"]:
#             priceUsdt = amountOut
#         if stableCoin in Token.STABLE_COINS.values():
#             stableCoinName = [k for k, v in Token.STABLE_COINS.items() if v == stableCoin][0]
#             priceStableCoin = amountOut
#             priceUsdt = (priceStableCoin * stableCoinPrices[stableCoinName])
            
                        
#         # print("BNB Price: " + str(priceStableCoin) + " in USDT: " + str(priceUsdt) )
        
#         return {
#                 "lastPrice" : lastPrice,
#                 "removeFromActivePairs" : removeFromActivePairs,
#                 "pairPrice" : PairPrice(currentTime=currentTime, pairAddress=pair.address, priceStableCoin=priceStableCoin, priceUsdt=priceUsdt, targetToken=targetToken, stableCoin=stableCoin)  
#             }
        
         
        
#     except Exception as err:
#         if "PancakeLibrary: INSUFFICIENT_LIQUIDITY" in str(err):
#             pass
#         else:
#             timeString = datetime.now().strftime("%H:%M:%S") 
#             print(f"{timeString}: Exception occured: {err}")
#         # pass


class FilterHoneypotV1:

    apiKey = ""
    # stableCoinPrices = dict()
    # targetTokenDecimals = dict()
    # lastPrice = dict()    
    
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
            

    # def updateStableCoinsToUSDTPrice(self):
    #     for stableCoinName in Token.STABLE_COINS:
    #         try:
    #             if stableCoinName == "USDT":
    #                 self.stableCoinPrices[stableCoinName] = 1
    #                 continue
    #             stableCoinToSell = web3.toWei("1", "ether")        
    #             router = web3.eth.contract( abi=pancakeswapRouterAbi, address=web3.toChecksumAddress(PANCAKESWAP_ROUTER_ADDRESS) )
    #             amountOut = router.functions.getAmountsOut(stableCoinToSell, [web3.toChecksumAddress(Token.STABLE_COINS[stableCoinName]) , web3.toChecksumAddress(Token.STABLE_COINS["USDT"])]).call()
    #             self.stableCoinPrices[stableCoinName] =  web3.fromWei(number=amountOut[1], unit='ether')
    #             print("\t%s price: %s" % (stableCoinName, str(self.stableCoinPrices[stableCoinName]) ))
    #         except Exception as err:
    #             timeString = datetime.now().strftime("%H:%M:%S") 
    #             print(f"{timeString}: Exception occured while updating {stableCoinName} price: {err}")
    #             pass
        

    def getActiveMinAgedPairList(self, minAge):        
        try:
            self.activeMinAgedPairs = self.store.getActivePairsMinAge(minAge, idsOnly=True)
        except Exception as err:
            timeString = datetime.now().strftime("%H:%M:%S") 
            print(f"{timeString}: Exception occured while getting active tokens: {err}")
            pass
        
    def getContextObject(self, pair):
        return {
            "pair": pair,
            "currentTime" : self.currentTime,
            # "targetTokenDecimals": self.targetTokenDecimals,
            # "stableCoinPrices" : self.stableCoinPrices,
            # "activePairs" : self.activeMinAgedPairs,
            # "lastPrice" : self.lastPrice
        }
    
    def filterForHoneyPots(self):    

        while True:
            try:            
                self.currentTime = datetime.now()
                print("Filtering on Honeypot V1: %s"%self.currentTime)
                start_time = time.time()
                minAge = '6 hours' # postgress interval value
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
                with mp.Pool(initializer=set_global_session, processes=1) as pool:
                    fetchFilterReturnList = pool.map(filterPairOnHoneypot, [self.getContextObject(pair) for pair in self.activeMinAgedPairs] )
                # asyncio.get_event_loop().run_until_complete(asyncio.gather(*(fetchTick(self.getContextObject(pair)) for pair in self.activeMinAgedPairs) ))
                
                # pairPriceList = []
                # for item in fetchTickReturnList:
                #     if item:
                #         if "pairPrice" in item:
                #             pairPriceList.append(item["pairPrice"])
                #         if "lastPrice" in item:
                #             for lastPriceUpdateKey in item["lastPrice"]:
                #                 if item["lastPrice"][lastPriceUpdateKey]:
                #                     self.lastPrice[lastPriceUpdateKey] = item["lastPrice"][lastPriceUpdateKey]
                #         if "removeFromActivePairs" in item:
                #             if len(item["removeFromActivePairs"]) > 0:
                #                 for pair in item["removeFromActivePairs"]:
                #                     self.activeMinAgedPairs.remove(pair)
                #                     self.store.markUnactive(pair)
                                    
                
                # self.store.storePairPriceList(pairPriceList)              
                
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
    filterHoneypotV1 = FilterHoneypotV1(os.environ.get('APITOKEN'))
    filterHoneypotV1.fetchPancakeSwapAbi()
    filterHoneypotV1.filterForHoneyPots()

if __name__ == "__main__":
    import time
    s = time.perf_counter()
    main()   
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
