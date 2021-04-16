def calc_rsi(candle_value, history, period=16):
  
  if history.size < period:
    return candle_value
  
  # print(period)
  # print(history)
  candle_value['analysis'] = {
    'rsi': {
      'period' : 16,
      'value' : 30
    }
  }
  return candle_value