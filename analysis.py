import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from math import sqrt
from typing import List, Dict


# ---------- I/O & helpers ----------
def load_data(csv_path: str) -> pd.DataFrame:
    """Load one fund CSV -> DataFrame with [date, nav_per_unit, short_name]."""
    df = pd.read_csv(csv_path)
    if "date" not in df.columns or "nav_per_unit" not in df.columns:
        raise ValueError(f"{csv_path} must contain columns: date, nav_per_unit (and optionally short_name).")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").drop_duplicates(subset="date").reset_index(drop=True)
    if "short_name" not in df.columns:
        df["short_name"] = Path(csv_path).stem.upper()
    return df[["date", "nav_per_unit", "short_name"]]


def span_years(dates: pd.Series) -> float:
    """Calendar years of coverage based on first/last dates (not row count)."""
    if dates.empty:
        return np.nan
    days = (dates.iloc[-1] - dates.iloc[0]).days
    return days / 365.25 if days > 0 else np.nan


def infer_periods_per_year(dates: pd.Series) -> float:
    """
    Infer average observations per year from the date series.
    Works even if a row is not a 'day' (funds have different dealing calendars).
    """
    yrs = span_years(dates)
    if not np.isfinite(yrs) or yrs <= 0:
        return np.nan
    return len(dates) / yrs


def period_return(df: pd.DataFrame, days: int) -> float:
    """
    Return over the last `days` ending at the last available date.
    Start NAV = nearest available NAV strictly before/at the start-date anchor.
    """
    if len(df) < 2:
        return np.nan
    end_nav = df["nav_per_unit"].iloc[-1]
    end_date = df["date"].iloc[-1]
    start_date = end_date - pd.Timedelta(days=days)
    start_idx = df["date"].searchsorted(start_date, side="left") - 1
    if start_idx < 0:
        return np.nan
    start_nav = df["nav_per_unit"].iloc[start_idx]
    return end_nav / start_nav - 1



