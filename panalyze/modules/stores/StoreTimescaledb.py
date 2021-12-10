import psycopg2
from psycopg2 import extras

from panalyze.models.Pair import Pair
from panalyze.models.PairPrice import PairPrice
from panalyze.models.Token import Token

DEFAULT_CONNECTION_STRING = "postgres://postgres:password@localhost:5432"
class StoreTimescaledb:

  def __init__(self):
    self.connection = None
    self.cur = None

  def connect(self, connectionString=None):  
    self.connectionString = connectionString or DEFAULT_CONNECTION_STRING
    self.connection = psycopg2.connect(self.connectionString)
    self.cur = self.connection.cursor()
    return self.connection

# --------------------
# EXISTS

  def checkPairExists(self, address):
    with self.connection:
      # self.cur.execute("SELECT address FROM assetvar_data.pair;")
      exists_query = '''
        select exists (
            SELECT 1
            FROM assetvar_data.pair
            WHERE address = %s
        )'''
      self.cur.execute (exists_query, (address,))
      return self.cur.fetchone()[0] 
  
  def checkTokenExists(self, address):
    with self.connection:
      exists_query = '''
        select exists (
            SELECT 1
            FROM assetvar_data.token
            WHERE tokenAddress = %s
        )'''
      self.cur.execute (exists_query, (address,))
      return self.cur.fetchone()[0] 
    
    
  # --------------------
  # GET ACTIVE
    
  def getActivePairs(self, idsOnly=True):
    with self.connection:
      if idsOnly:
        self.cur.execute("SELECT address, token0Address, token1Address FROM assetvar_data.view_active_pair;")
        return [Pair(address=item[0], token0=item[1], token1=item[2] ) for item in self.cur.fetchall()] 
      else:
        self.cur.execute("SELECT * FROM assetvar_data.view_active_pair ;")
        return [Pair(address=item[0], token0=item[1], token1=item[2] ) for item in self.cur.fetchall()] 
  
  def getActivePairsMinAge(self, minAge, idsOnly=True, limit=None):
    with self.connection:
      if idsOnly:
        queryString = "SELECT address, token0Address, token1Address FROM assetvar_data.view_active_pair where starttime < NOW() - INTERVAL '%s' "% minAge
        if limit:
          queryString += " limit %s"%limit
        queryString += ";"
        self.cur.execute(queryString)
        return [Pair(address=item[0], token0=item[1], token1=item[2] ) for item in self.cur.fetchall()] 
      else:
        queryString = "SELECT * FROM assetvar_data.view_active_pair "
        if limit:
          queryString += " limit %s"%limit
        queryString += ";"
        self.cur.execute(queryString)
        return [Pair(address=item[0], token0=item[1], token1=item[2] ) for item in self.cur.fetchall()] 
  
  # Not used yet
  def getActiveTokens(self, idsOnly=True):
    with self.connection:
      if idsOnly:
        self.cur.execute("SELECT tokenAddress FROM assetvar_data.view_active_token;")
        return [Token(tokenAddress=item[0] ) for item in self.cur.fetchall()] 
      else:
        self.cur.execute("SELECT * FROM assetvar_data.view_active_token ;")
        return [Token(tokenAddress=item[0] ) for item in self.cur.fetchall()] 
    

  # --------------------
  # STORE ABSTRACTS    

  def storeToken(self, token):
    if not self.checkTokenExists(token.tokenAddress):
      with self.connection:
        self.cur.execute("INSERT INTO assetvar_data.token(tokenAddress, name, symbol, decimals, startTime, endTime, atBlockNr, atBlockHash, transactionIndex, transactionHash, totalSupply ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
          (
            token.tokenAddress,
            token.name,
            token.symbol,
            token.decimals,
            token.startTime,
            token.endTime,
            token.atBlockNr,
            token.atBlockHash.hex(),
            token.transactionIndex,
            token.transactionHash.hex(),
            token.totalSupply
          )
        )
        self.connection.commit()
  

  def storePair(self, pair):
    if not self.checkPairExists(pair.address):
      self.storeToken(pair.token0)
      self.storeToken(pair.token1)
      with self.connection:
        self.cur.execute("INSERT INTO assetvar_data.pair(address, token0Address, token1Address, startTime, endTime, atBlockNr, atBlockHash, transactionIndex, transactionHash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
          (
            pair.address,
            pair.token0.tokenAddress,
            pair.token1.tokenAddress,
            pair.startTime,
            pair.endTime,
            pair.atBlockNr,
            pair.atBlockHash.hex(),
            pair.transactionIndex,
            pair.transactionHash.hex()
          )
        )
      self.connection.commit()
    else: # do some update?
      pass
  
  # --------------------
  # PAIR PRICE
  
  def storePairPriceList(self, PairPriceList):
    with self.connection:
      insert_query = 'INSERT INTO assetvar_data.pair_price(currentTime, pairAddress, priceStableCoin, priceUsdt, targetToken, stableCoin) VALUES %s'
      extras.execute_values (
          self.cur, insert_query, [(pairPrice.currentTime, pairPrice.pairAddress, pairPrice.priceStableCoin, pairPrice.priceUsdt, pairPrice.targetToken, pairPrice.stableCoin) for pairPrice in PairPriceList if pairPrice], template=None, page_size=100
      )
      
    self.connection.commit()
    
  def getPairPrices(self, pair):
    with self.connection:
      self.cur.execute("SELECT currentTime, pairAddress, priceStableCoin, priceUsdt, targetToken, stableCoin FROM assetvar_data.pair_price WHERE pairAddress = %s;", (pair.address,))
      return [PairPrice(currentTime=item[0], pairAddress=item[1], priceStableCoin=item[2], priceUsdt=item[3], targetToken=item[4], stableCoin=item[5] ) for item in self.cur.fetchall()] 
  
  # --------------------
  # GET BY
    
  def getPairByAddress(self, address):
    with self.connection:
      query = '''
            SELECT token0Address, token1Address, address, startTime, endTime, atBlockNr, atBlockHash, transactionIndex, transactionHash
            FROM assetvar_data.pair
            WHERE address = %s;
      '''
      self.cur.execute (query, (address,))
      returnData = self.cur.fetchone()
      if returnData:
        return Pair(token0=returnData[0], token1=returnData[1], address=returnData[2], startTime=returnData[3], endTime=returnData[4], atBlockNr=returnData[5], atBlockHash=returnData[6], transactionIndex=returnData[7], transactionHash=returnData[8])
  
  def getTokenByAddress(self, address):
    with self.connection:
      query = '''
            SELECT tokenAddress, name, symbol, decimals, startTime, endTime, atBlockNr, atBlockHash, transactionIndex, transactionHash, totalSupply, lastUpdated
            FROM assetvar_data.token
            WHERE tokenAddress = %s;
      '''
      self.cur.execute (query, (address,))
      returnData = self.cur.fetchone()
      if returnData:
        return Token(tokenAddress=returnData[0], name=returnData[1], symbol=returnData[2], decimals=returnData[3], startTime=returnData[4], endTime=returnData[5], atBlockNr=returnData[6], atBlockHash=returnData[7], transactionIndex=returnData[8], transactionHash=returnData[9], totalSupply=returnData[10], lastUpdated=returnData[11])
  
   
          
  # --------------------
  # FILTERS
    
  def filterTokenActive(self, token, reason, toFilter=True):
    with self.connection:
      self.cur.execute("INSERT INTO assetvar_data.filter_token_active(tokenAddress, toFilter, failedAttempts, reason) VALUES (%s, %s, %s, %s) ON CONFLICT (tokenAddress) DO UPDATE SET failedAttempts = EXCLUDED.failedAttempts + 1",
          (
            token.tokenAddress,
            toFilter,
            1,
            reason
          )
        )
    self.connection.commit()
  
  def filterTokenHoneypotv1(self, token, reason, toFilter=True, reasonDetails=None):
    with self.connection:
      self.cur.execute("INSERT INTO assetvar_data.filter_token_honeypot_v1(tokenAddress, toFilter, failedAttempts, reason, reasonDetails) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (tokenAddress) DO UPDATE SET failedAttempts = EXCLUDED.failedAttempts + 1;",
          (
            token.tokenAddress,
            toFilter,
            1,
            reason,
            reasonDetails
          )
        )
    self.connection.commit()
      
    
  # --------------------
  # META DATA UPDATES
  
  def updateTokenTax(self, token, buyTax, selTax):
    with self.connection:
      self.cur.execute("INSERT INTO assetvar_data.token_tax(tokenAddress, buyTax, sellTax) VALUES (%s, %s, %s) ON CONFLICT (tokenAddress) DO NOTHING;",
          (
            token.tokenAddress,
            buyTax,
            selTax
          )
        )
    self.connection.commit()
  
  def updateTokenGasSellUsed(self, token, buyGasUsed, sellGasUsed):
    with self.connection:
      self.cur.execute("INSERT INTO assetvar_data.token_gas_used(tokenAddress, buyGasUsed, sellGasUsed) VALUES (%s, %s, %s) ON CONFLICT (tokenAddress) DO NOTHING;",
          (
            token.tokenAddress,
            buyGasUsed, 
            sellGasUsed
          )
        )
    self.connection.commit()
    

