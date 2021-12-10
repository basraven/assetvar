DROP TABLE  IF EXISTS assetvar_data.filter_token_honeypot_v1;
CREATE TABLE assetvar_data.filter_token_honeypot_v1 (
  tokenAddress        CHAR(42)          NOT NULL,
  toFilter            BOOLEAN           NOT NULL,
  failedAttempts      INTEGER           NULL,
  reason              INTEGER           NOT NULL,
  reasonDetails       VARCHAR           NULL,
  lastUpdated         TIMESTAMP         DEFAULT NOW(),
  PRIMARY KEY (tokenAddress)
);
-- Reason: toFilter
--    101: No,  no specific reason (don't use)
--    102: No,  TRANSFER_FAILED
--    103: No,  Tax is 0.0
--    104: No,  execution reverted

--    501: Yes, no specific reason (don't use)
--    502: Yes, INSUFFICIENT_LIQUIDITY
--    503: Yes, TRANSFER_FROM_FAILED
--    504: Yes, high tax
--    505: Yes, high sell gas