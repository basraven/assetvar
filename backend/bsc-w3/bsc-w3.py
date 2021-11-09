import json
import requests
import time

import warnings
#source: https://paohuee.medium.com/interact-binance-smart-chain-using-python-4f8d745fe7b7

from web3 import Web3
warnings.filterwarnings("ignore", message="divide by zero encountered in divide")

web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
print(web3.isConnected())
pair_abi = ""

def printDetails(addr, abi):
    print("Getting details for: ", addr)
    url_eth = "https://api.bscscan.com/api"
    contract_address = web3.toChecksumAddress(addr)
    API_ENDPOINT = url_eth+"?module=contract&action=getabi&address="+str(contract_address)
    API_ENDPOINT += "&apikey=<APIKEY>"
    # r = requests.get(url = API_ENDPOINT)
    # response = r.json()
    # print(response)
    # token_abi=json.loads(response["result"])
    pair_abi = abi
    contract = web3.eth.contract(address=contract_address, abi=pair_abi)
    totalSupply = contract.functions.totalSupply().call()
    print("Total Supply", totalSupply)
    print("Contract Name", contract.functions.name().call())
    print("Contract Symbol", contract.functions.symbol().call())
    



def bla():
    # PF factory
    FactoryAddress = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
    url_eth = "https://api.bscscan.com/api"
    contract_address = web3.toChecksumAddress(FactoryAddress)
    API_ENDPOINT = url_eth+"?module=contract&action=getabi&address="+str(contract_address)
    API_ENDPOINT += "&apikey=<APIKEY>"
    r = requests.get(url = API_ENDPOINT)
    response = r.json()
    factory_abi=json.loads(response["result"])


    contract = web3.eth.contract(address=contract_address, abi=factory_abi)
    # totalSupply = contract.functions.totalSupply().call()
    # print(totalSupply)
    # print(contract.functions.name().call())
    # print(contract.functions.symbol().call())


    # address = web3.toChecksumAddress(MyAddress)
    # balance=contract.functions.balanceOf(address).call()
    # print(web3.fromWei(balance, "ether"))


    BUSD = web3.toChecksumAddress("0xe9e7cea3dedca5984780bafc599bd69add087d56")
    WBNB = web3.toChecksumAddress("0x844fa82f1e54824655470970f7004dd90546bb28")
    InputTokenAddr = BUSD
    OutputTokenAddr = WBNB
    pancake_factory_address = web3.toChecksumAddress(FactoryAddress)

    # print(pancake_factory_address)
    # exit
    contract = web3.eth.contract(address=pancake_factory_address, abi=factory_abi)
    pair_address = contract.functions.getPair(InputTokenAddr,OutputTokenAddr).call()

    print("PAIR Address: ", pair_address)

    # pair address abi
    url_eth = "https://api.bscscan.com/api"
    contract_address = web3.toChecksumAddress(pair_address)
    API_ENDPOINT = url_eth+"?module=contract&action=getabi&address="+str(contract_address)
    API_ENDPOINT += "&apikey=<APIKEY>"
    r = requests.get(url = API_ENDPOINT)
    response = r.json()
    pair_abi=json.loads(response["result"])


    pair1 = web3.eth.contract(abi=pair_abi, address=pair_address)
    reserves = pair1.functions.getReserves().call()
    reserve0 = reserves[0]
    reserve1 = reserves[1]
    print(f"The current price is : ${reserve0/reserve1}")






    contract = web3.eth.contract(address=FactoryAddress, abi=factory_abi)
    accounts = web3.eth.accounts
    paircreated_Event = contract.events.PairCreated() # Modification

    def handle_event(event):
        receipt = web3.eth.waitForTransactionReceipt(event['transactionHash'])
        result = paircreated_Event.processReceipt(receipt) # Modification
        print(result[0]['args'])
        printDetails(result[0]['args'].token0, pair_abi)

    def log_loop(event_filter, poll_interval):
        while True:
            for event in event_filter.get_new_entries():
                handle_event(event)
                time.sleep(poll_interval)

    
    warnings.filterwarnings('ignore', '.*The event signature did not match the provided ABI.*', )
    block_filter = web3.eth.filter({'fromBlock':'latest', 'address': FactoryAddress})
    log_loop(block_filter, 2)

bla()