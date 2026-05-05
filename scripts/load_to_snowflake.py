import snowflake.connector
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    return snowflake.connector.connect(
        user=os.getenv("SF_USER"),
        password=os.getenv("SF_PASSWORD"),
        account=os.getenv("SF_ACCOUNT"),
        database="STOCK_ANALYTICS",
        schema="RAW",
        warehouse="COMPUTE_WH"
    )

def load_dataframe(cursor, df, table):
    # Insert rows one batch at a time
    rows = [tuple(row) for row in df.itertuples(index=False)]
    placeholders = ", ".join(["%s"] * len(df.columns))
    query = f"INSERT INTO {table} VALUES ({placeholders})"
    cursor.executemany(query, rows)
    print(f"OK {len(rows)} rows inserted into {table}")

def main():
    print("Connecting to Snowflake...")
    conn = get_connection()
    cur = conn.cursor()

    # Truncate tables before reload
    cur.execute("TRUNCATE TABLE STOCK_ANALYTICS.RAW.STOCK_PRICES")
    cur.execute("TRUNCATE TABLE STOCK_ANALYTICS.RAW.MACRO_INDICATORS")
    print("OK Tables truncated")

    # Load stock prices
    print("Loading stock prices...")
    stocks = pd.read_csv("data/raw/stock_prices.csv")
    stocks["date"] = pd.to_datetime(stocks["date"]).dt.date
    load_dataframe(cur, stocks, "STOCK_ANALYTICS.RAW.STOCK_PRICES")

    # Load macro indicators
    print("Loading macro indicators...")
    macro = pd.read_csv("data/raw/macro_indicators.csv")
    macro["date"] = pd.to_datetime(macro["date"]).dt.date
    macro = macro.dropna()
    load_dataframe(cur, macro, "STOCK_ANALYTICS.RAW.MACRO_INDICATORS")

    conn.commit()
    cur.close()
    conn.close()
    print("Done. All data loaded successfully.")

if __name__ == "__main__":
    main()