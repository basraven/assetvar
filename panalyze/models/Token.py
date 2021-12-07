class Token:
        
    STABLE_COINS = {
        "BNB"  : "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        "USDT" : "0x55d398326f99059fF775485246999027B3197955",
        "BUSD" : "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
        "CAKE" : "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
        "BTCB" : "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c"
    }

    tokenAddress = None
    name = None
    symbol = None
    decimals = None
    startTime = None
    endTime = None
    atBlockNr = None
    atBlockHash = None
    transactionIndex = None
    transactionHash = None
    totalSupply = None
    lastUpdated = None 
    
    def __init__(self, tokenAddress = None, name = None, symbol = None, decimals = None, startTime = None, endTime = None, atBlockNr = None, atBlockHash = None, transactionIndex = None, transactionHash = None, totalSupply = None, lastUpdated = None):
        self.tokenAddress = tokenAddress
        self.name = name
        self.symbol = symbol
        self.decimals = decimals
        self.startTime = startTime
        self.endTime = endTime
        self.atBlockNr = atBlockNr
        self.atBlockHash = atBlockHash
        self.transactionIndex = transactionIndex
        self.transactionHash = transactionHash
        self.totalSupply = totalSupply
        self.lastUpdated = lastUpdated