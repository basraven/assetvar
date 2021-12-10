DROP VIEW IF EXISTS view_filter_stats_token_honeypot_v1;
CREATE VIEW view_filter_stats_token_honeypot_v1 as

SELECT toFilter, reason,  COUNT(*)
, ( (COUNT(*) / SUM(COUNT(*)) OVER ()) * 100) AS "% of total"
FROM
  filter_token_honeypot_v1
GROUP BY (tofilter, reason )
ORDER BY "% of total" DESC
;