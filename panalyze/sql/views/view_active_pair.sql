DROP VIEW IF EXISTS view_active_pair;
CREATE VIEW view_active_pair as

SELECT *
FROM pair 
WHERE NOT EXISTS (
   SELECT toFilter 
   FROM   filter_token_honeypot_v1
   WHERE  (
            filter_token_honeypot_v1.tokenAddress 			= pair.token0address
        OR  filter_token_honeypot_v1.tokenAddress 			= pair.token1address
   )    AND filter_token_honeypot_v1.toFilter               = true
)
AND	  NOT EXISTS (
   SELECT toFilter 
   FROM   filter_token_active
   WHERE  (
            filter_token_active.tokenAddress 	            = pair.token0address
        OR  filter_token_active.tokenAddress 	            = pair.token1address
   )    AND filter_token_active.toFilter                    = true
)
;	