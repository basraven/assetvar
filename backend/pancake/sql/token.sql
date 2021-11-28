DROP TABLE  IF EXISTS assetvar_data.token;
CREATE TABLE assetvar_data.token (
  tokenAddress        CHAR(42)          NOT NULL,
  name                VARCHAR(128)      NOT NULL,
  symbol              VARCHAR(64)       NOT NULL,
  decimals            INT               NULL,
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

