
class Techanalyzer:

  def __init__(self):
    self.connection = None
    self.cur = None

  def analyze(self, candle_value):
    candle_value['analysis'] = {
      'rsi': {
        'period' : 16,
        'value' : 30
      }
    }
    return candle_value