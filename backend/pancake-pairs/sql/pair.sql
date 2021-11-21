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

