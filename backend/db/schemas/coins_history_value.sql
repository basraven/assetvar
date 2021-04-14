DROP TABLE coins_history_value;
CREATE TABLE coins_history_value (
  starttime           TIMESTAMPTZ       NOT NULL,
  endtime             TIMESTAMPTZ       NOT NULL,
  pair_name           TEXT              NOT NULL,
  interval            TEXT              NOT NULL,
  first_trade_id      TEXT              NOT NULL,
  last_trade_id       TEXT              NOT NULL,
  open                DOUBLE PRECISION  NOT NULL,
  close               DOUBLE PRECISION  NOT NULL,
  high                DOUBLE PRECISION  NOT NULL,
  low                 DOUBLE PRECISION  NOT NULL,
  base_asset_volume   DOUBLE PRECISION  NOT NULL,
  quote_asset_volume  DOUBLE PRECISION  NOT NULL,
  number_of_trades    DOUBLE PRECISION  NOT NULL,
  is_kline_close      boolean
);

SELECT create_hypertable('coins_history_value', 'starttime');
