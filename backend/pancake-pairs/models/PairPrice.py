class PairPrice:

    currentTime = None
    pairAddress = None
    priceBnb = None 
    priceUsdt = None 
    targetToken = None
    swappableToken = None
    
    def __init__(self, currentTime = None, pairAddress = None, priceBnb = None, priceUsdt = None, targetToken = None, swappableToken = None):
        self.currentTime = currentTime
        self.pairAddress = pairAddress
        self.priceBnb = priceBnb
        self.priceUsdt = priceUsdt
        self.targetToken = targetToken
        self.swappableToken = swappableToken
