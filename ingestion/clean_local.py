import duckdb

def clean():
    con = duckdb.connect()
    con.execute("""
        COPY (
            SELECT
                CAST(date AS DATE) AS date,
                store_id,
                sku_id,
                GREATEST(qty_sold, 0) AS qty_sold,
                GREATEST(stock_on_hand, 0) AS stock_on_hand
            FROM read_csv_auto('data/sample/pos_transactions.csv')
            WHERE store_id IS NOT NULL AND sku_id IS NOT NULL
        ) TO 'data/sample/pos_clean.parquet' (FORMAT PARQUET)
    """)
    print("Cleaned data written to data/sample/pos_clean.parquet")

if __name__ == "__main__":
    clean()