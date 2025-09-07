import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from math import sqrt
from typing import List, Dict
import seaborn as sns


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
    return days / 365 if days > 0 else np.nan


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


# ---------- Single-fund metrics ----------
def compute_metrics_single(df: pd.DataFrame, rf_annual: float = 0.03) -> Dict[str, float]:
    """
    Metrics: CAGR, Vol (annualized), Sharpe, MaxDD, Calmar, 1M/3M/6M/YTD/1Y.
    Annualization uses inferred observations/year (not fixed 252).
    """
    df = df.copy()
    df["ret"] = df["nav_per_unit"].pct_change()
    # clip to damp data glitches; keeps method robust to sparse/irregular calendars
    df["ret_clean"] = df["ret"].clip(-0.5, 0.5)

    years = span_years(df["date"])
    cagr = (df["nav_per_unit"].iloc[-1] / df["nav_per_unit"].iloc[0]) ** (1 / years) - 1 if years and years > 0 else np.nan

    periods_per_year = infer_periods_per_year(df["date"])
    if not np.isfinite(periods_per_year) or periods_per_year <= 0:
        periods_per_year = 252.0  # safe fallback

    mu = df["ret_clean"].mean(skipna=True)
    sd = df["ret_clean"].std(skipna=True, ddof=1)
    vol_annual = sd * sqrt(periods_per_year) if pd.notna(sd) else np.nan

    rf_period = (1 + rf_annual) ** (1 / periods_per_year) - 1
    sharpe = ((mu - rf_period) / sd) * sqrt(periods_per_year) if (sd and sd > 0) else np.nan

    cum_max = df["nav_per_unit"].cummax()
    drawdown = df["nav_per_unit"] / cum_max - 1.0
    max_dd = drawdown.min() if not drawdown.empty else np.nan
    calmar = (cagr / abs(max_dd)) if (pd.notna(cagr) and pd.notna(max_dd) and max_dd != 0) else np.nan

    # YTD: anchor at Jan-01 using nearest available NAV before/at that anchor
    today = df["date"].iloc[-1]
    ytd_start = pd.Timestamp(year=today.year, month=1, day=1)
    ytd_idx = df["date"].searchsorted(ytd_start, side="left") - 1
    ytd = df["nav_per_unit"].iloc[-1] / df["nav_per_unit"].iloc[ytd_idx] - 1 if ytd_idx >= 0 else np.nan

    return {
        "start_date": df["date"].iloc[0].date(),
        "end_date": df["date"].iloc[-1].date(),
        "years": round(years, 3) if pd.notna(years) else np.nan,
        "obs_per_year": round(periods_per_year, 2),
        "cagr": cagr,
        "vol_annual": vol_annual,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "calmar": calmar,
        "ret_1m": period_return(df, 30),
        "ret_3m": period_return(df, 90),
        "ret_6m": period_return(df, 180),
        "ret_ytd": ytd,
        "ret_1y": period_return(df, 365),
    }


# ---------- Peer comparison with ≥1 calendar year requirement ----------
def compare_funds(file_paths: List[str], rf_annual: float = 0.03) -> pd.DataFrame:
    """
    Build a ranking table for funds that have at least 1 calendar year of history (>= 365 days span).
    Funds failing the requirement are dropped (not evaluated).
    """
    rows = []
    dropped = []

    for path in file_paths:
        df = load_data(path)
        yrs = span_years(df["date"])
        if not np.isfinite(yrs) or yrs < 1.0:
            dropped.append((df["short_name"].iloc[0], yrs))
            continue  # enforce ≥ 1 year coverage

        m = compute_metrics_single(df, rf_annual=rf_annual)
        rows.append({"fund": df["short_name"].iloc[0], **m})

    rank_df = pd.DataFrame(rows)
    if rank_df.empty:
        return rank_df  # nothing to compare

    # nice column order
    cols = [
        "fund", "start_date", "end_date", "years", "obs_per_year",
        "cagr", "vol_annual", "sharpe", "max_drawdown", "calmar",
        "ret_1m", "ret_3m", "ret_6m", "ret_ytd", "ret_1y"
    ]
    rank_df = rank_df[cols].sort_values(by=["sharpe", "cagr"], ascending=[False, False], na_position="last").reset_index(drop=True)

    if dropped:
        # attach a note for your notebook to inspect
        rank_df.attrs["dropped_funds"] = dropped

    return rank_df


# ---------- Plotting (bar charts only; no line charts) ----------
def bar_rank(df: pd.DataFrame, col: str, title: str):
    """
    Horizontal bar ranking for a metric across funds.
    Handles percent-like columns for labeling in %.
    """
    if df is None or df.empty or col not in df.columns:
        print(f"No data to plot for {col}.")
        return

    data = df[["fund", col]].dropna().copy()
    if data.empty:
        print(f"No data to plot for {col}.")
        return

    pct_like = col in ["cagr", "vol_annual", "max_drawdown", "ret_1m", "ret_3m", "ret_6m", "ret_ytd", "ret_1y"]
    values = data[col] * 100 if pct_like else data[col]
    order = values.sort_values(ascending=False).index
    values = values.loc[order]
    labels = data["fund"].loc[order]

    plt.figure()
    plt.barh(labels, values)
    plt.title(title)
    plt.xlabel("Percent (%)" if pct_like else col)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
    
def load_index_data(
    csv_path: str,
    min_months_first_year: int = 3,
    min_years: int = 2
) -> pd.DataFrame:
    """
    Load index CSV -> DataFrame with [date, nav_per_unit, short_name].
    Use column 'close' as nav_per_unit.
    Only return DataFrame if:
      - First valid year has at least `min_months_first_year` months of data.
      - Index exists for at least `min_years` years (from the first valid year onward).
    Otherwise, return empty DataFrame.
    """
    df = pd.read_csv(csv_path)
    if "time" not in df.columns or "close" not in df.columns:
        raise ValueError(f"{csv_path} must contain columns: time, close")

    df = df.rename(columns={"time": "date", "close": "nav_per_unit"})
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").drop_duplicates(subset="date").reset_index(drop=True)
    df["short_name"] = Path(csv_path).stem.upper()

    # Check conditions
    years = sorted(set(df["date"].dt.year))
    if not years:
        return pd.DataFrame()

    valid_start_year = None
    for yr in years:
        year_df = df[df["date"].dt.year == yr]
        if year_df.empty:
            continue
        months = (year_df["date"].iloc[-1] - year_df["date"].iloc[0]).days / 30.44
        if months >= min_months_first_year:
            valid_start_year = yr
            break

    if valid_start_year is None:
        return pd.DataFrame()

    valid_years = [yr for yr in years if yr >= valid_start_year]
    if len(valid_years) < min_years:
        return pd.DataFrame()

    return df[["date", "nav_per_unit", "short_name"]]

    

def yearly_comparison_multi_index(
    fund_paths: List[str],
    index_paths: List[str]
) -> pd.DataFrame:
    """
    Compare funds with multiple indexes on a yearly basis.
    Assumes load_data / load_index_data already filter out invalid funds or indexes.
    Each index will have 2 columns: return_x and beat_x (x = index name).
    """
    # Load all indexes
    index_dfs = {}
    for path in index_paths:
        df = load_index_data(path)
        if df.empty:
            continue
        df = df.set_index("date")
        name = df["short_name"].iloc[0]
        index_dfs[name] = df

    results = []

    for path in fund_paths:
        fund_df = load_data(path)
        if fund_df.empty:
            continue
        fund_df = fund_df.set_index("date")
        fund_name = fund_df["short_name"].iloc[0]

        years = sorted(set(fund_df.index.year))

        for yr in years:
            fund_year = fund_df[fund_df.index.year == yr]
            if fund_year.empty:
                continue

            row = {"fund": fund_name, "year": yr}

            # Fund return
            fund_start = fund_year["nav_per_unit"].iloc[0]
            fund_end = fund_year["nav_per_unit"].iloc[-1]
            row["fund_return"] = fund_end / fund_start - 1

            # Compare with each index
            for idx_name, idx_df in index_dfs.items():
                idx_year = idx_df[idx_df.index.year == yr]
                if idx_year.empty:
                    row[f"return_{idx_name}"] = None
                    row[f"beat_{idx_name}"] = None
                else:
                    idx_start = idx_year["nav_per_unit"].iloc[0]
                    idx_end = idx_year["nav_per_unit"].iloc[-1]
                    idx_ret = idx_end / idx_start - 1
                    row[f"return_{idx_name}"] = idx_ret
                    row[f"beat_{idx_name}"] = row["fund_return"] > idx_ret

            results.append(row)

    return pd.DataFrame(results)


def plot_yearly_heatmap(df: pd.DataFrame, index_name: str):
    """
    Plot yearly heatmap for beat_index.
    ✓ = fund outperformed, ✗ = fund underperformed, empty = no data.
    """
    col = f"beat_{index_name.upper()}"
    if col not in df.columns:
        print(f"Column {col} not found")
        return

    df = df.copy()
    df["year"] = df["year"].astype(int)

    # Normalize: handle True/False/None or string equivalents
    def normalize(x):
        if x is True or str(x) == "True":
            return True
        if x is False or str(x) == "False":
            return False
        return np.nan

    df[col] = df[col].map(normalize)

    # Pivot table (fund x year)
    pivot = df.pivot_table(index="fund", columns="year", values=col, aggfunc="first")

    # Debug print
    print("Pivot sample:\n", pivot.head())

    if pivot.empty or pivot.dropna(how="all").empty:
        print("No valid data to plot heatmap.")
        return

    # Annotation symbols
    annot = pivot.applymap(lambda x: "✓" if x is True else ("✗" if x is False else ""))

    # Numeric values for seaborn
    pivot_num = pivot.applymap(lambda x: 1 if x is True else (0 if x is False else np.nan))

    if pivot_num.dropna(how="all").empty:
        print("All values are NaN after conversion.")
        return

    plt.figure(figsize=(12, max(4, len(pivot) * 0.4)))
    sns.heatmap(
        pivot_num,
        cmap=["#ff4d4d", "#4caf50"],  # red = underperformed, green = outperformed
        cbar=False,
        linewidths=0.5,
        linecolor="grey",
        annot=annot,
        fmt="s"
    )
    plt.title(f"Beat {index_name.upper()} by year (✓ = win, ✗ = lose)")
    plt.ylabel("Fund")
    plt.xlabel("Year")
    plt.tight_layout()
    plt.show()