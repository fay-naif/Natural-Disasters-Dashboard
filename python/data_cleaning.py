"""
Natural disasters data checks and preparation.

Reads the cleaned CSV inside data/Natural_Disasters_Clean_AR.zip, runs the
data quality checks, confirms every country has a continent and
prints the headline figures used in the dashboard.

Run from the repository root:
    pip install -r python/requirements.txt
    python python/data_cleaning.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "Natural_Disasters_Clean_AR.zip"
OUT = ROOT / "python" / "output"

BASE_COLUMNS = [
    "Disaster_ID", "Date", "Year", "Month", "Country", "Disaster_Type",
    "Deaths", "People_Affected", "Economic_Loss_USD", "Data_Status",
]
IMPACT = ["Deaths", "People_Affected", "Economic_Loss_USD"]


def load():
    df = pd.read_csv(DATA, compression="zip", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


def quality_checks(df):
    base = df[BASE_COLUMNS]
    text_cols = [c for c in base.columns if pd.api.types.is_string_dtype(base[c])]
    checks = {
        "Records": len(df),
        "Blank cells": int(base.isna().sum().sum()),
        "Duplicate records": int(base.duplicated().sum()),
        "Duplicate Disaster_ID": int(df["Disaster_ID"].duplicated().sum()),
        "Invalid dates": int(df["Date"].isna().sum()),
        "Year not matching Date": int((df["Date"].dt.year != df["Year"]).sum()),
        "Month not matching Date": int((df["Date"].dt.month != df["Month"]).sum()),
        "Negative impact values": int((df[IMPACT] < 0).sum().sum()),
        "Cells with surrounding whitespace": int(
            sum((base[c] != base[c].str.strip()).sum() for c in text_cols)
        ),
        "Countries without a continent": int(df["Continent"].isna().sum()),
    }
    return pd.Series(checks, name="Result")


def headline(df):
    return pd.Series(
        {
            "Disasters": len(df),
            "Deaths": int(df["Deaths"].sum()),
            "People affected": int(df["People_Affected"].sum()),
            "Economic loss (USD)": int(df["Economic_Loss_USD"].sum()),
            "Countries affected": df["Country"].nunique(),
            "Years": f"{df['Year'].min()}-{df['Year'].max()}",
        },
        name="Value",
    )


def by_type(df):
    g = df.groupby("Disaster_Type").agg(
        disasters=("Disaster_ID", "count"),
        deaths=("Deaths", "sum"),
        people_affected=("People_Affected", "sum"),
        economic_loss_usd=("Economic_Loss_USD", "sum"),
    )
    return g.sort_values("disasters", ascending=False)


def main():
    df = load()
    checks = quality_checks(df)
    OUT.mkdir(parents=True, exist_ok=True)
    checks.to_csv(OUT / "quality_checks.csv", header=True)
    by_type(df).to_csv(OUT / "summary_by_type.csv")

    print("Data quality checks")
    print(checks.to_string())
    print()
    print("Headline figures")
    print(headline(df).to_string())
    print()
    print("By disaster type")
    print(by_type(df).to_string())
    print()
    print("Disasters by continent")
    print(df["Continent"].value_counts().to_string())


if __name__ == "__main__":
    main()
