import psycopg2

CONNECTION_STRING = "postgres://postgres:password@192.168.6.69:5432/assetvar"
class Store:

  def __init__(self):
    self.connection = None
    self.cur = None

  def connect(self):  
    self.connection = psycopg2.connect(CONNECTION_STRING)
    self.cur = self.connection.cursor()
    return self.connection

    
  def save_candle(self, candle_value, commit=True):
    # try:
    self.cur.execute("INSERT INTO assetvar_data.coins_history_value(starttime, endtime, pair_name, interval, first_trade_id, last_trade_id, open, close, high, low, base_asset_volume, quote_asset_volume, number_of_trades, is_kline_close) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s );",
        (
          candle_value["starttime"],
          candle_value["endtime"],
          candle_value["pair_name"],
          candle_value["interval"],
          candle_value["first_trade_id"],
          candle_value["last_trade_id"],
          candle_value["open"],
          candle_value["close"],
          candle_value["high"],
          candle_value["low"],
          candle_value["base_asset_volume"],
          candle_value["quote_asset_volume"],
          candle_value["number_of_trades"],
          candle_value["is_kline_close"]
        )
    )
    if commit:
      self.connection.commit()
    # except (Exception, psycopg2.Error) as error:
    #   print(error.pgerror)
 
  def save_analysis(self, analyzed_candle, commit=True):
    if 'analysis' not in analyzed_candle:
      return
    for analysis_key, analyzed_value in analyzed_candle['analysis'].items():
      
      # try:
      query_header = "INSERT INTO assetvar_data.technical_%s(starttime, endtime, pair_name, interval, %s_period, %s)" % (
        analysis_key,
        analysis_key,
        analysis_key
      )
      self.cur.execute( query_header + "VALUES (%s, %s, %s, %s, %s, %s);",
          (
            analyzed_candle["starttime"],
            analyzed_candle["endtime"],
            analyzed_candle["pair_name"],
            analyzed_candle["interval"],
            analyzed_value['period'],
            analyzed_value['value']
          )
      )
      if commit:
        self.connection.commit()
      # except (Exception, psycopg2.Error) as error:
      #   print(error.pgerror)

  