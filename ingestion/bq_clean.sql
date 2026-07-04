CREATE OR REPLACE TABLE `restockiq.pos_clean` AS
SELECT
  DATE(date) AS date,
  store_id,
  sku_id,
  GREATEST(qty_sold, 0) AS qty_sold,
  GREATEST(stock_on_hand, 0) AS stock_on_hand
FROM `restockiq.pos_transactions`
WHERE store_id IS NOT NULL AND sku_id IS NOT NULL;