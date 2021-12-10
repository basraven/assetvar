DROP TABLE  IF EXISTS assetvar_data.token_gas_used;
CREATE TABLE assetvar_data.token_gas_used (
  tokenAddress        CHAR(42)          NOT NULL,
  buyGasUsed          DECIMAL           NULL,
  sellGasUsed         DECIMAL           NULL,
  lastUpdated         TIMESTAMP         DEFAULT NOW(),
  PRIMARY KEY (tokenAddress)
);