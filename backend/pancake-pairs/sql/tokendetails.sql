DROP TABLE  IF EXISTS assetvar_data.token;
CREATE TABLE assetvar_data.token (
  tokenAddress        CHAR(42)          NOT NULL,
  name                VARCHAR(128)      NOT NULL,
  symbol              VARCHAR(64)       NOT NULL,
  startTime           TIMESTAMP       DEFAULT NOW(),
  endTime             TIMESTAMP       ,
  atBlockNr           DECIMAL           NOT NULL,
  atBlockHash         VARCHAR(128)      NOT NULL,
  transactionIndex    DECIMAL           NOT NULL,
  transactionHash     VARCHAR(128)      NOT NULL,
  totalSupply         DECIMAL           NOT NULL,
  active              boolean           DEFAULT true,
  lastUpdated         TIMESTAMP       DEFAULT NOW(),
  PRIMARY KEY (tokenAddress)
);


DROP TABLE  IF EXISTS assetvar_data.pair;
CREATE TABLE assetvar_data.pair (
  address             CHAR(42)          NOT NULL,
  token0Address       CHAR(42)          NOT NULL,
  token1Address       CHAR(42)          NOT NULL,
  startTime           TIMESTAMP       DEFAULT NOW(),
  endTime             TIMESTAMP       ,
  atBlockNr           DECIMAL           NOT NULL,
  atBlockHash         VARCHAR(128)      NOT NULL,
  transactionIndex    DECIMAL           NOT NULL,
  transactionHash     VARCHAR(128)      NOT NULL,
  active              boolean           DEFAULT true,
  lastUpdated         TIMESTAMP       DEFAULT NOW(),
  PRIMARY KEY (address)
);

DROP TABLE  IF EXISTS assetvar_data.pair_price;
CREATE TABLE assetvar_data.pair_price (
  currentTime         TIMESTAMP       ,
  pairAddress         CHAR(42)          NOT NULL,
  priceBnb            DECIMAL           NOT NULL,
  priceUsdt           DECIMAL           NOT NULL,
  targetToken         CHAR(42)          NOT NULL,
  swappableToken      CHAR(42)          NOT NULL,
  PRIMARY KEY (currentTime, pairAddress)
);
