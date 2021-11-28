from modules.techanalysis import techanalysis_rsi

class Techanalyzer:

  def __init__(self):
    self.connection = None
    self.cur = None

  def analyze(self, candle_value, history):
    
    history_current_pair = history[(history.pair_name == candle_value['pair_name'])]
    candle_value = techanalysis_rsi.calc_rsi(candle_value, history_current_pair)
    print(candle_value)
    return candle_value