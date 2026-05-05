import yfinance as yf
import pandas as pd
from pathlib import Path

TICKERS = ["AAPL", "TSLA", "MC.PA", "TTE.PA", "MSFT", "AMZN"]
START = "2020-01-01"
END   = "2024-12-31"

def fetch_stock_prices():
    print("Telechargement des prix d'actions...")

    raw = yf.download(TICKERS, start=START, end=END, auto_adjust=True)

    prices = raw["Close"].copy()
    prices = prices.reset_index()
    prices = prices.melt(id_vars="Date", var_name="ticker", value_name="close_price")
    prices = prices.rename(columns={"Date": "date"})
    prices = prices.dropna(subset=["close_price"])
    prices["date"] = pd.to_datetime(prices["date"]).dt.date

    output = Path("data/raw/stock_prices.csv")
    prices.to_csv(output, index=False)

    print(f"OK {len(prices)} lignes sauvegardees dans {output}")
    print(f"  Periode : {prices['date'].min()} -> {prices['date'].max()}")
    print(f"  Tickers : {sorted(prices['ticker'].unique())}")
    return prices

if __name__ == "__main__":
    df = fetch_stock_prices()
    print(df.head(12))