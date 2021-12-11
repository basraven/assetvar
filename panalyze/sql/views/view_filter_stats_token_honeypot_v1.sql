DROP VIEW IF EXISTS assetvar_data.view_filter_stats_token_honeypot_v1;
CREATE VIEW assetvar_data.view_filter_stats_token_honeypot_v1 as

SELECT toFilter, reason,  COUNT(*)
, ( (COUNT(*) / SUM(COUNT(*)) OVER ()) * 100) AS "% of total"
FROM
  assetvar_data.filter_token_honeypot_v1
GROUP BY (tofilter, reason )
ORDER BY "% of total" DESC
;