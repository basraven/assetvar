DROP TABLE  IF EXISTS assetvar_data.pair_price;
CREATE TABLE assetvar_data.pair_price (
  currentTime         TIMESTAMP       ,
  pairAddress         CHAR(42)          NOT NULL,
  priceStableCoin     DECIMAL           NOT NULL,
  priceUsdt           DECIMAL           NOT NULL,
  targetToken         CHAR(42)          NOT NULL,
  stableCoin         CHAR(42)          NOT NULL,
  PRIMARY KEY (currentTime, pairAddress)
);
