DROP TABLE  IF EXISTS assetvar_data.token;
CREATE TABLE assetvar_data.token (
  tokenAddress        CHAR(42)          NOT NULL,
  name                VARCHAR(128)      NOT NULL,
  symbol              VARCHAR(64)       NOT NULL,
  startTime           TIMESTAMPTZ       DEFAULT NOW(),
  endTime             TIMESTAMPTZ       ,
  atBlockNr           DECIMAL           NOT NULL,
  atBlockHash         VARCHAR(128)      NOT NULL,
  transactionIndex    DECIMAL           NOT NULL,
  transactionHash     VARCHAR(128)      NOT NULL,
  totalSupply         DECIMAL           NOT NULL,
  active              boolean           DEFAULT true,
  lastUpdated         TIMESTAMPTZ       DEFAULT NOW(),
  PRIMARY KEY (tokenAddress)
);


DROP TABLE  IF EXISTS assetvar_data.pair;
CREATE TABLE assetvar_data.pair (
  address             CHAR(42)          NOT NULL,
  token0Address       CHAR(42)          NOT NULL,
  token1Address       CHAR(42)          NOT NULL,
  startTime           TIMESTAMPTZ       DEFAULT NOW(),
  endTime             TIMESTAMPTZ       ,
  atBlockNr           DECIMAL           NOT NULL,
  atBlockHash         VARCHAR(128)      NOT NULL,
  transactionIndex    DECIMAL           NOT NULL,
  transactionHash     VARCHAR(128)      NOT NULL,
  active              boolean           DEFAULT true,
  lastUpdated         TIMESTAMPTZ       DEFAULT NOW(),
  PRIMARY KEY (address)
);
