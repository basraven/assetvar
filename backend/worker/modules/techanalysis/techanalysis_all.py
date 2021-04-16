from modules.techanalysis import techanalysis_rsi

class Techanalyzer:

  def __init__(self):
    self.connection = None
    self.cur = None

  def analyze(self, candle_value, history):
    
    techanalysis_rsi.calc_rsi(candle_value, history)
    # print(candle_value)
    return candle_value