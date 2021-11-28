from pyalgotrade import strategy
from pyalgotrade.barfeed import quandlfeed
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade import bar
import pandas as pd
import numpy as np


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(MyStrategy, self).__init__(feed)
        self.__instrument = instrument

    def onBars(self, bars):
        bar = bars[self.__instrument]
        self.info(bar.getClose())

# # Load the bar feed from the CSV file
# feed = quandlfeed.Feed()
# feed.addBarsFromCSV("orcl", "./WIKI-ORCL-2000-quandl.csv")

high = np.random.uniform(low=0.5, high=1, size=(5,))
low = np.random.uniform(low=0.01, high=0.5, size=(5,))
vol = np.random.uniform(low=8, high=10000, size=(5,))

data = {
    'Open': low,
    'High' : high,
    'Low' :low,
    'Close': high,
    'Adj Close': high,
    'Volume': vol,
    'ExtraCol1': vol
}  

# df = pd.DataFrame(index=pd.date_range(start='2021-11-01', end='2021-11-05'), columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'ExtraCol1'], data=np.random.rand(5, 7))
df = pd.DataFrame(index=pd.date_range(start='2021-11-01', end='2021-11-05'), columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'ExtraCol1'], data=data)

print(df)
feed = yahoofeed.Feed()
feed.addBarsFromSequence('orcl', df.index.map(lambda i:
        bar.BasicBar(
            i,      
            df.loc[i, 'Open'],
            df.loc[i, 'High'],            
            df.loc[i, 'Low'],             
            df.loc[i, 'Close'],           
            df.loc[i, 'Volume'],          
            df.loc[i, 'Adj Close'],           
            bar.Frequency.DAY,        
            df.loc[i, 'ExtraCol1':].to_dict())    
).values)

# Evaluate the strategy with the feed's bars.
myStrategy = MyStrategy(feed, "orcl")
myStrategy.run()