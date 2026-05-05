import pandas as pd
from pathlib import Path

INDICATORS = {
    "CPI"      : "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL",
    "FEDFUNDS" : "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS",
    "UNRATE"   : "https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE",
}

def fetch_macro_indicators():
    print("Téléchargement des indicateurs macro (FRED)...")
    frames = []

    for indicator, url in INDICATORS.items():
        df = pd.read_csv(url)                        # pas de parse_dates
        df.columns = ["date", "value"]               # renommer directement
        df["date"] = pd.to_datetime(df["date"])      # convertir ensuite

        df = df[df["date"] >= "2020-01-01"]
        df = df[df["date"] <= "2024-12-31"]
        df["date"] = df["date"].dt.date
        df["indicator"] = indicator

        frames.append(df[["date", "indicator", "value"]])
        print(f"  OK {indicator} : {len(df)} lignes")

    result = pd.concat(frames, ignore_index=True)

    output = Path("data/raw/macro_indicators.csv")
    result.to_csv(output, index=False)

    print(f"\nOK {len(result)} lignes totales sauvegardées dans {output}")
    return result

if __name__ == "__main__":
    df = fetch_macro_indicators()
    print(df.groupby("indicator").agg({"value": "count"}))