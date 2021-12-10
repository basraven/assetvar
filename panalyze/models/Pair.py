class Pair:

    token0 = None
    token1 = None
    address = None 
    startTime = None
    endTime = None
    atBlockNr = None
    atBlockHash = None
    transactionIndex = None
    transactionHash = None

    def __init__(self, token0 = None, token1 = None, address = None, startTime = None, endTime = None, atBlockNr = None, atBlockHash = None, transactionIndex = None, transactionHash = None):
        self.token0 = token0 
        self.token1 = token1 
        self.address = address 
        self.startTime = startTime
        self.endTime = endTime
        self.atBlockNr = atBlockNr
        self.atBlockHash = atBlockHash
        self.transactionIndex = transactionIndex
        self.transactionHash = transactionHash