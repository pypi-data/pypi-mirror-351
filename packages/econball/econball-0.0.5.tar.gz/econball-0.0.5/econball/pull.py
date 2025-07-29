"""The pull function for fetching the economic data."""

import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import pandas as pd
import tqdm

from .coinbase import pull as coinbase_pull
from .data import Data
from .fred import pull as fred_pull
from .yfinance import pull as yfinance_pull

_DEFAULT_MANIFEST = {
    str(Data.FRED): {
        "ECBESTRVOLWGTTRMDMNRT": True,  # Euro Short-Term Rate: Volume-Weighted Trimmed Mean Rate
        "SOFR30DAYAVG": True,  # 30-Day Average SOFR
        "SOFR": True,  # Secured Overnight Financing Rate"
        "ADPWNUSNERSA": True,  # Total Nonfarm Private Payroll Employment
        "GDP": True,  # Gross Domestic Product
        "ECIWAG": True,  # Employment Cost Index: Wages and Salaries: Private Industry Workers
        "NFCI": True,  # Chicago Fed National Financial Conditions Index
        "EFFR": True,  # Effective Federal Funds Rate
        "DTP10J28": True,  # 10-Year 0.5% Treasury Inflation-Indexed Note
        "AMERIBOR": True,  # Overnight Unsecured AMERIBOR Benchmark Interest Rate
        "SOFR90DAYAVG": True,  # 90-Day Average SOFR
        "SOFRVOL": True,  # Secured Overnight Financing Volume
        "DFEDTARU": True,  # Federal Funds Target Range - Upper Limit
        "IUDSOIA": True,  # Daily Sterling Overnight Index Average (SONIA) Rate
        "BBKMGDP": True,  # Brave-Butters-Kelley Real Gross Domestic Product
        "ECBDFR": True,  # ECB Deposit Facility Rate for Euro Area
    },
    str(Data.YFINANCE): {
        "MSFT": True,  # Microsoft
        "NVDA": True,  # NVIDIA
    },
    str(Data.COINBASE): {
        "BTC-USD": True,  # Bitcoin
    },
}
_DATA_PROVIDERS = {
    str(Data.FRED): fred_pull,
    str(Data.YFINANCE): yfinance_pull,
    str(Data.COINBASE): coinbase_pull,
}


def pull(
    manifest: dict[str, dict[str, Any]] | None = None,
    min_date: datetime.date | None = None,
) -> pd.DataFrame:
    """Pull the latest economic data."""
    if manifest is None:
        manifest = _DEFAULT_MANIFEST
    series_pool = []
    with ThreadPoolExecutor() as executor:
        futures = []
        for k, v in _DEFAULT_MANIFEST.items():
            futures.extend([executor.submit(_DATA_PROVIDERS[k], x) for x in v])
        for future in tqdm.tqdm(as_completed(futures), desc="Downloading"):
            series_pool.extend(future.result())
    df = pd.concat(series_pool, axis=1).sort_index().asfreq("D", method="ffill").ffill()
    if min_date is not None:
        df = df[df.index >= min_date]
    return df
