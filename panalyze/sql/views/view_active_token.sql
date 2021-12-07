DROP VIEW IF EXISTS view_active_token;
CREATE VIEW view_active_token as

SELECT *
FROM token 
WHERE   NOT EXISTS (
   SELECT toFilter 
   FROM   filter_token_honeypot_v1
   WHERE  (
            filter_token_honeypot_v1.tokenAddress 			   = token.tokenaddress
   )    AND filter_token_honeypot_v1.toFilter                    = true
)
AND	    NOT EXISTS (
   SELECT toFilter 
   FROM   filter_token_active
   WHERE  (
            filter_token_active.tokenAddress 	            = token.tokenaddress
   )    AND filter_token_active.toFilter                    = true
)
;	