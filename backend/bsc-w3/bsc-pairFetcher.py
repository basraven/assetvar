import json
import requests
import time
import asyncio

import warnings
#source: https://paohuee.medium.com/interact-binance-smart-chain-using-python-4f8d745fe7b7

from web3 import Web3
warnings.filterwarnings("ignore", message="divide by zero encountered in divide")

web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
print(web3.isConnected())

class PairFetcher:

    apiKey = ""

    PANCAKESWAP_FACTORY_ADDRESS = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
    pancakeswapFactoryAbi = ""

    BSCSCAN_API = "https://api.bscscan.com/api"

    def __init__(self, apikey):
        self.apiKey = apikey
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
        return json.loads(response["result"])

    def getPairDetails(self, contract, abi):
        contract_address = web3.toChecksumAddress(contract)
        contract = web3.eth.contract(address=contract_address, abi=abi)
        totalSupply = contract.functions.totalSupply().call()
        print("Total Supply", totalSupply)
        print("Contract Name", contract.functions.name().call())
        print("Contract Symbol", contract.functions.symbol().call())

    # async def fetchPairUpdate(self):
        # address = "0x6897CBB72834A1586154EE6b68a114cc5311f2B6"
        # self.getPairDetails(address, await self.getAbi(address))
    
    async def fetchPairUpdates(self):
        contract = web3.eth.contract(address=self.PANCAKESWAP_FACTORY_ADDRESS, abi=self.pancakeswapFactoryAbi)
        paircreated_Event = contract.events.PairCreated() # Modification


        async def handle_event(event):
            receipt = web3.eth.waitForTransactionReceipt(event['transactionHash'])
            result = paircreated_Event.processReceipt(receipt) # Modification
            print(result[0]['args'])
            # printDetails(result[0]['args'].token0, pair_abi)

        
        warnings.filterwarnings('ignore', '.*The event signature did not match the provided ABI.*', )
        block_filter = web3.eth.filter({'fromBlock':'latest', 'address': self.PANCAKESWAP_FACTORY_ADDRESS})
        # log_loop(block_filter, 2)


        async def periodic(event_filter):
            while True:
                for event in event_filter.get_new_entries():
                    await handle_event(event)
                await asyncio.sleep(1)

        # def stop():
        #     task.cancel()
        loop = asyncio.get_event_loop()
        # loop.call_later(5, stop)
        task = loop.create_task(periodic(block_filter))

        await task

    #     # address = web3.toChecksumAddress(MyAddress)
    #     # balance=contract.functions.balanceOf(address).call()
    #     # print(web3.fromWei(balance, "ether"))


    #     BUSD = web3.toChecksumAddress("0xe9e7cea3dedca5984780bafc599bd69add087d56")
    #     WBNB = web3.toChecksumAddress("0x844fa82f1e54824655470970f7004dd90546bb28")
    #     InputTokenAddr = BUSD
    #     OutputTokenAddr = WBNB
    #     pancake_factory_address = web3.toChecksumAddress(FactoryAddress)

    #     # print(pancake_factory_address)
    #     # exit
    #     contract = web3.eth.contract(address=pancake_factory_address, abi=factory_abi)
    #     pair_address = contract.functions.getPair(InputTokenAddr,OutputTokenAddr).call()

    #     print("PAIR Address: ", pair_address)

    #     # pair address abi
    #     url_eth = "https://api.bscscan.com/api"
    #     contract_address = web3.toChecksumAddress(pair_address)
    #     API_ENDPOINT = url_eth+"?module=contract&action=getabi&address="+str(contract_address)
    #     API_ENDPOINT += "&apikey=<APIKEY>"
    #     r = requests.get(url = API_ENDPOINT)
    #     response = r.json()
    #     pair_abi=json.loads(response["result"])


    #     pair1 = web3.eth.contract(abi=pair_abi, address=pair_address)
    #     reserves = pair1.functions.getReserves().call()
    #     reserve0 = reserves[0]
    #     reserve1 = reserves[1]
    #     print(f"The current price is : ${reserve0/reserve1}")






    #     contract = web3.eth.contract(address=FactoryAddress, abi=factory_abi)
    #     accounts = web3.eth.accounts
    #     paircreated_Event = contract.events.PairCreated() # Modification

    #     def handle_event(event):
    #         receipt = web3.eth.waitForTransactionReceipt(event['transactionHash'])
    #         result = paircreated_Event.processReceipt(receipt) # Modification
    #         print(result[0]['args'])
    #         printDetails(result[0]['args'].token0, pair_abi)

    #     def log_loop(event_filter, poll_interval):
    #         while True:
    #             for event in event_filter.get_new_entries():
    #                 handle_event(event)
    #                 time.sleep(poll_interval)

        
    #     warnings.filterwarnings('ignore', '.*The event signature did not match the provided ABI.*', )
    #     block_filter = web3.eth.filter({'fromBlock':'latest', 'address': FactoryAddress})
    #     log_loop(block_filter, 2)

async def main():
    pairFetcher = PairFetcher("<APIKEY>")
    await pairFetcher.fetchPancakeSwapAbi()
    await pairFetcher.fetchPairUpdates()

if __name__ == "__main__":
    import time
    s = time.perf_counter()
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        pass
    
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
