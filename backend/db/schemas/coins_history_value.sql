DROP TABLE  IF EXISTS assetvar_data.coins_history_value;
-- CREATE SCHEMA assetvar_data;
CREATE TABLE assetvar_data.coins_history_value (
  starttime           TIMESTAMPTZ       NOT NULL,
  endtime             TIMESTAMPTZ       NOT NULL,
  pair_name           VARCHAR(24)       NOT NULL,
  interval            VARCHAR(24)        NOT NULL,
  first_trade_id      VARCHAR(24)       NOT NULL,
  last_trade_id       VARCHAR(24)       NOT NULL,
  open                DOUBLE PRECISION  NOT NULL,
  close               DOUBLE PRECISION  NOT NULL,
  high                DOUBLE PRECISION  NOT NULL,
  low                 DOUBLE PRECISION  NOT NULL,
  base_asset_volume   DOUBLE PRECISION  NOT NULL,
  quote_asset_volume  DOUBLE PRECISION  NOT NULL,
  number_of_trades    DOUBLE PRECISION  NOT NULL,
  is_kline_close      boolean,
  PRIMARY KEY (endtime, pair_name, interval)
);

-- SELECT create_hypertable('assetvar_data.coins_history_value', 'endtime');
