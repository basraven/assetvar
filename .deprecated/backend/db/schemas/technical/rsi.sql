DROP TABLE IF EXISTS assetvar_data.technical_rsi;
CREATE TABLE assetvar_data.technical_rsi (
  starttime           TIMESTAMPTZ       NOT NULL,
  endtime             TIMESTAMPTZ       NOT NULL,
  pair_name           VARCHAR(24)       NOT NULL,
  interval            VARCHAR(24)       NOT NULL,
  rsi_period          DOUBLE PRECISION  NOT NULL,
  rsi                 DOUBLE PRECISION  NOT NULL,
  PRIMARY KEY (endtime, pair_name, interval, rsi_period),
  -- CONSTRAINT  (endtime, pair_name, interval)
    FOREIGN KEY(endtime, pair_name, interval) 
	    REFERENCES assetvar_data.coins_history_value(endtime, pair_name, interval)
);

-- SELECT create_hypertable('assetvar_data.technical_rsi', 'endtime');
