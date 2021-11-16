class Token:
    
    STABLE_TOKENS = [
        
    ]
    tokenAddress = None
    name = None
    symbol = None
    startTime = None
    endTime = None
    atBlockNr = None
    atBlockHash = None
    transactionIndex = None
    transactionHash = None
    totalSupply = None
    active = None
    lastUpdated = None 
    
    def __init__(self, tokenAddress = None, name = None, symbol = None, startTime = None, endTime = None, atBlockNr = None, atBlockHash = None, transactionIndex = None, transactionHash = None, totalSupply = None, active = None, lastUpdated = None):
        self.tokenAddress = tokenAddress
        self.name = name
        self.symbol = symbol
        self.startTime = startTime
        self.endTime = endTime
        self.atBlockNr = atBlockNr
        self.atBlockHash = atBlockHash
        self.transactionIndex = transactionIndex
        self.transactionHash = transactionHash
        self.totalSupply = totalSupply
        self.active = active
        self.lastUpdated = lastUpdated