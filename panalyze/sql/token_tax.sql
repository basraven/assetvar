DROP TABLE  IF EXISTS assetvar_data.token_tax;
CREATE TABLE assetvar_data.token_tax (
  tokenAddress        CHAR(42)          NOT NULL,
  buyTax              DECIMAL           NOT NULL,
  sellTax             DECIMAL           NOT NULL,
  lastUpdated         TIMESTAMP         DEFAULT NOW(),
  PRIMARY KEY (tokenAddress)
);