DROP TABLE  IF EXISTS assetvar_data.filter_token_active;
CREATE TABLE assetvar_data.filter_token_active (
  tokenAddress        CHAR(42)          NOT NULL,
  toFilter            BOOLEAN           NOT NULL,
  failedAttempts      INTEGER           NULL,
  reason               INTEGER           NOT NULL,
  lastUpdated         TIMESTAMP         DEFAULT NOW(),
  PRIMARY KEY (tokenAddress)
);
-- reason:
--    0: No, just use
--    1: Yes, no specific reason
--    2: Not a known stable coin