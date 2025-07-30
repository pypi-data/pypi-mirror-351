-- Create a stream from the enriched transactions topic
CREATE STREAM IF NOT EXISTS tx_json WITH (
  KAFKA_TOPIC='tx_enriched',
  VALUE_FORMAT='JSON',
  TIMESTAMP='ts'
);

-- Create a table for card failure counts in 60-second windows
CREATE TABLE IF NOT EXISTS card_fail_60s WITH (
  KAFKA_TOPIC='card_fail_60s',
  VALUE_FORMAT='JSON'
) AS
SELECT 
  card_id,
  HOP_START(ROWTIME, INTERVAL '5 SECONDS', INTERVAL '60 SECONDS') AS window_start,
  HOP_END(ROWTIME, INTERVAL '5 SECONDS', INTERVAL '60 SECONDS') AS window_end,
  COUNT(*) AS fail_cnt
FROM tx_json
WHERE status='DECLINED'
GROUP BY card_id
EMIT CHANGES;

-- Create a table for unique IP addresses per card in 60-second windows
CREATE TABLE IF NOT EXISTS card_ip_uniques_60s WITH (
  KAFKA_TOPIC='card_ip_uniques_60s',
  VALUE_FORMAT='JSON'
) AS
SELECT 
  card_id,
  HOP_START(ROWTIME, INTERVAL '5 SECONDS', INTERVAL '60 SECONDS') AS window_start,
  HOP_END(ROWTIME, INTERVAL '5 SECONDS', INTERVAL '60 SECONDS') AS window_end,
  COUNT_DISTINCT(ip->addr) AS uniq_ips
FROM tx_json
GROUP BY card_id
EMIT CHANGES;

-- Print a confirmation message
PRINT 'Feature windows created successfully' LIMIT 1;
