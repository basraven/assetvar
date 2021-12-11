DROP VIEW IF EXISTS assetvar_data.view_active_token;
CREATE VIEW assetvar_data.view_active_token as

SELECT *
FROM assetvar_data.token 
WHERE   NOT EXISTS (
   SELECT toFilter 
   FROM   assetvar_data.filter_token_honeypot_v1
   WHERE  (
            filter_token_honeypot_v1.tokenAddress 			   = token.tokenaddress
   )    AND filter_token_honeypot_v1.toFilter                    = true
)
AND	    NOT EXISTS (
   SELECT toFilter 
   FROM   assetvar_data.filter_token_active
   WHERE  (
            filter_token_active.tokenAddress 	            = token.tokenaddress
   )    AND filter_token_active.toFilter                    = true
)
;	