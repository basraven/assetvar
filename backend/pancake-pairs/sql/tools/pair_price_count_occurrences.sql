SELECT pairaddress, COUNT(currenttime) AS count
FROM pair_price
GROUP BY pairaddress
ORDER BY COUNT DESC;
