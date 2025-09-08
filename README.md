# Open Fund Analysis

## Overview
This project provides tools to **analyze Vietnamese open-ended funds** and compare their performance against benchmarks such as **VNINDEX** or ETFs. It automates **data collection, cleaning, and evaluation** of funds using financial metrics, yearly comparisons, and ranking methods.

The pipeline supports:
- Fetching NAV data of all bond, balanced, and stock funds from **VnStock API**.
- Retrieving benchmark index/ETF data.
- Computing financial performance metrics (CAGR, Sharpe ratio, Calmar ratio, volatility, drawdowns, etc.).
- Comparing funds against multiple benchmarks on a **yearly basis**.
- Generating **beat summaries** (e.g., Fund A beats VNINDEX 3/5 years = 60%).
- Ranking funds based on composite scoring with adjustable weights.
- Visualization with **bar charts** and **yearly heatmaps**.

---

## Repository Structure
```
.
├── analysis.py             # Core analytics and plotting functions
├── fetch_all_open_funds.py # Script to fetch and save NAV data for all funds
├── take_data.py            # Data collection utilities (funds, indexes, stocks)
├── demo_analysis.ipynb     # Example analysis workflow
├── take_data.ipynb         # Notebook for data collection and inspection
└── data/                   # Local directory for storing CSV files
```

---

## Features

### 1. Data Collection
- **Funds**: Automatically fetches NAV reports for all open-ended funds, categorized into:
  - Bond funds
  - Balanced funds
  - Stock funds
- **Indexes/ETFs**: Fetches historical close prices for stock indexes or ETF symbols.

Scripts:
- `fetch_all_open_funds.py`: downloads NAV data of all available funds into `data/`.
- `take_data.py`: provides `OpenData` class and helper functions for retrieving fund/index data.

### 2. Fund Metrics
Implemented in `analysis.py`:
- CAGR
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Calmar ratio
- Period returns: 1M, 3M, 6M, YTD, 1Y

### 3. Comparisons
- **Yearly fund vs index comparison** (`yearly_comparison_multi_index`)
- **Beat summary**: counts and percentages of outperformance
- **Composite ranking**: combines metrics and beat ratios with user-defined weights

### 4. Visualization
- **Bar charts**: fund rankings by metric
- **Heatmaps**: yearly outperformance vs. benchmarks

---

## Installation
### Requirements
- Python 3.8+
- Packages:
  ```bash
  pip install pandas numpy matplotlib seaborn vnstock
  ```

---

## Usage

### 1. Fetch fund data
```bash
python fetch_all_open_funds.py
```
This downloads bond, balanced, and stock fund NAV data into `data/`.

### 2. Analyze funds
Example in **`demo_analysis.ipynb`**:
```python
from analysis import compare_funds, yearly_comparison_multi_index, beat_summary_multi, rank_funds_multi

# Compare performance metrics
files = glob("data/stock_fund/*.csv")
metrics_df = compare_funds(files)

# Compare against VNINDEX
index_files = ["data/index/VNINDEX.csv"]
yearly_df = yearly_comparison_multi_index(files, index_files)

# Summarize beating ratio
beat_df = beat_summary_multi(yearly_df, ["VNINDEX"])

# Final ranking
rank_df = rank_funds_multi(metrics_df, beat_df, ["VNINDEX"])
print(rank_df)
```

### 3. Visualization
```python
from analysis import bar_rank, plot_yearly_heatmap

bar_rank(metrics_df, "sharpe", "Sharpe Ratios")
plot_yearly_heatmap(yearly_df, "VNINDEX")
```

---

## Example Output
- **Fund metrics table** with CAGR, Sharpe, Calmar.
- **Beat summary** like:
  ```
  Fund    beat_VNINDEX   beat_pct_VNINDEX
  F1      3/5            60.0
  F2      2/4            50.0
  ```
- **Ranking** with composite scores.

---

## Next Steps
- Extend support for more benchmarks (VN30, ETFs).
- Add deep learning experiments for fund ranking prediction.
- Deploy as a dashboard (e.g., Streamlit/Power BI integration).
