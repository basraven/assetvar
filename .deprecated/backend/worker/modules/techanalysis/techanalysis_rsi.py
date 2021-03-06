import pandas as pd
import math

def calc_rsi(candle_value, history, period=16):
  
  if len(history.index) < period:
    return candle_value
  

  """See source https://github.com/peerchemist/finta
  and fix https://www.tradingview.com/wiki/Talk:Relative_Strength_Index_(RSI)
  Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements.
  RSI oscillates between zero and 100. Traditionally, and according to Wilder, RSI is considered overbought when above 70 and oversold when below 30.
  Signals can also be generated by looking for divergences, failure swings and centerline crossovers.
  RSI can also be used to identify the general trend."""

  delta = history["close"].diff()

  up, down = delta.copy(), delta.copy()
  up[up < 0] = 0
  down[down > 0] = 0

  _gain = up.ewm(com=(period - 1), min_periods=period).mean()
  _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()

  RS = _gain / _loss
  rsi_series = pd.Series(100 - (100 / (1 + RS)), name="RSI")
  rsi_value = rsi_series.iloc[-1]
  if not math.isnan(rsi_value):
    candle_value['analysis'] = {
      'rsi': {
        'period' : period,
        'value' : rsi_value
      }
    }
  return candle_value