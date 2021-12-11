DROP VIEW IF EXISTS assetvar_data.view_active_pair;
CREATE VIEW assetvar_data.view_active_pair as

SELECT *
FROM assetvar_data.pair 
WHERE NOT EXISTS (
   SELECT toFilter 
   FROM   assetvar_data.filter_token_honeypot_v1
   WHERE  (
            filter_token_honeypot_v1.tokenAddress 			= pair.token0address
        OR  filter_token_honeypot_v1.tokenAddress 			= pair.token1address
   )    AND filter_token_honeypot_v1.toFilter               = true
)
AND	  NOT EXISTS (
   SELECT toFilter 
   FROM   assetvar_data.filter_token_active
   WHERE  (
            filter_token_active.tokenAddress 	            = pair.token0address
        OR  filter_token_active.tokenAddress 	            = pair.token1address
   )    AND filter_token_active.toFilter                    = true
)
;	