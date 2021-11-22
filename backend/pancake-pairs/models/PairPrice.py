class PairPrice:

    currentTime = None
    pairAddress = None
    priceStableCoin = None 
    priceUsdt = None 
    targetToken = None
    stableCoin = None
    
    def __init__(self, currentTime = None, pairAddress = None, priceStableCoin = None, priceUsdt = None, targetToken = None, stableCoin = None):
        self.currentTime = currentTime
        self.pairAddress = pairAddress
        self.priceStableCoin = priceStableCoin
        self.priceUsdt = priceUsdt
        self.targetToken = targetToken
        self.stableCoin = stableCoin
