"""data_loader.py — Load and validate delivery data."""

import pandas as pd
from pathlib import Path
from utils import load_config


def load_raw(path: str = None) -> pd.DataFrame:
    """Load raw delivery CSV and apply basic type casting."""
    if path is None:
        cfg  = load_config()
        path = Path(__file__).resolve().parent.parent / cfg["paths"]["raw_data"]
    df = pd.read_csv(path, parse_dates=["date"])
    df["month_num"] = df["date"].dt.month
    df["on_time"]   = (df["delay_min"] == 0).astype(int)
    return df


def validate(df: pd.DataFrame) -> None:
    """Run basic data quality checks and print a summary."""
    assert df["delivery_id"].nunique() == len(df), "Duplicate delivery IDs found"
    assert df["delay_min"].min() >= 0,              "Negative delay minutes found"
    assert df["customer_satisfaction"].between(1, 5).all(), "CSAT out of 1–5 range"
    print(f"Data validated: {len(df)} rows, {df['region'].nunique()} regions, "
          f"{df['driver_id'].nunique()} drivers.")
    print(f"    Date range: {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"    Missing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")


if __name__ == "__main__":
    df = load_raw()
    validate(df)
