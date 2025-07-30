# Aroleid Simple Strategy Prototyper

A Python package for backtesting trading strategies with OHLCV data, designed for rapid strategy prototyping and testing with futures contracts.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Development Status](https://img.shields.io/badge/status-pre--alpha-red.svg)](https://pypi.org/project/aroleid-simple-strategy-prototyper/)

---

## ⚠️ Legal Disclaimer

**THE INFORMATION PROVIDED IS FOR EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY. IT DOES NOT CONSTITUTE FINANCIAL, INVESTMENT, OR TRADING ADVICE. TRADING INVOLVES SUBSTANTIAL RISK, AND YOU MAY LOSE MORE THAN YOUR INITIAL INVESTMENT.**

**THIS SOFTWARE AND ITS DOCUMENTATION ARE PROVIDED "AS IS," WITHOUT ANY WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. THE AUTHORS AND COPYRIGHT HOLDERS ASSUME NO LIABILITY FOR ANY CLAIMS, DAMAGES, OR OTHER LIABILITIES ARISING FROM THE USE OR DISTRIBUTION OF THIS SOFTWARE. USE AT YOUR OWN RISK.**

**Licensed under the GNU General Public License v3.0 (GPL-3.0). See the [LICENSE](LICENSE) for details.**

---

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Core Concepts](#core-concepts)
- [Detailed Tutorials](#detailed-tutorials)
- [Development](#development)

## Quick Start

```python
import aroleid_simple_strategy_prototyper as assp
import pandas as pd

# Define your strategy
class MyStrategy(assp.Backtester):
    def add_indicators(self) -> None:
        # Add a 100-period simple moving average
        self._market_data_df["00_sma_100"] = (
            self._market_data_df["close"].rolling(window=100).mean()
        )
    
    def strategy(self, row: pd.Series) -> None:
        # Strategy logic will be implemented here
        # (Currently a stub - order execution not yet implemented)
        pass

# Run backtest
backtester = MyStrategy()
backtester.load_historical_market_data("path/to/your/data.csv", symbol="MNQZ4")
backtester.set_initial_cash(100_000)
backtester.set_contract_specifications(
    symbol="MNQ", point_value=2.0, tick_size=0.25,
    broker_commission_per_contract=0.25, exchange_fees_per_contract=0.37
)
backtester.run_backtest()
```

## Installation

### From PyPI (Recommended)

```bash
pip install aroleid-simple-strategy-prototyper
```

### For Google Colab

```python
!pip install aroleid-simple-strategy-prototyper

# Optional: Mount Google Drive for CSV access
from google.colab import drive
drive.mount('/content/drive')
```

### Development Installation

```bash
git clone https://github.com/nilskujath/aroleid_simple_strategy_prototyper.git
cd aroleid_simple_strategy_prototyper
poetry install
```

## Basic Usage

### 1. Import and Setup Logging

```python
import aroleid_simple_strategy_prototyper as assp
import pandas as pd
import logging

# Optional: Enable debug logging
logging.getLogger("aroleid_simple_strategy_prototyper").setLevel(logging.DEBUG)
```

### 2. Create Your Strategy Class

```python
class MyStrategy(assp.Backtester):
    def add_indicators(self) -> None:
        # Define your technical indicators here
        self._market_data_df["00_sma_20"] = (
            self._market_data_df["close"].rolling(window=20).mean()
        )
        self._market_data_df["01_rsi"] = self._calculate_rsi(period=14)
    
    def strategy(self, row: pd.Series) -> None:
        # Define your trading logic here
        # Note: Order execution is not yet implemented
        pass
    
    def _calculate_rsi(self, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = self._market_data_df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
```

### 3. Load Data and Configure

```python
# Instantiate your strategy
backtester = MyStrategy()

# Load historical market data (Databento CSV format)
backtester.load_historical_market_data(
    path_to_dbcsv="path/to/your/data.csv",
    symbol="MNQZ4"  # Optional symbol filter
)

# Set initial capital
backtester.set_initial_cash(100_000)

# Define contract specifications
backtester.set_contract_specifications(
    symbol="MNQ",                           # Contract symbol
    point_value=2.0,                        # Dollar value per point
    tick_size=0.25,                         # Minimum price increment
    broker_commission_per_contract=0.25,    # Broker fees per contract
    exchange_fees_per_contract=0.37         # Exchange fees per contract
)
```

### 4. Run Backtest

```python
# Execute the backtest
backtester.run_backtest()
```

## Core Concepts

### Architecture

The package is built around a single abstract base class `Backtester` that encapsulates the entire backtesting workflow. Users implement custom strategies by subclassing `Backtester` and defining two required methods:

- `add_indicators()`: Calculate technical indicators
- `strategy()`: Define trading logic (currently a stub)

### Data Flow

1. **Load Data**: Historical OHLCV data in Databento CSV format
2. **Configure**: Set initial cash and contract specifications  
3. **Add Indicators**: Calculate technical indicators automatically
4. **Execute Strategy**: Process each bar through your trading logic
5. **Generate Results**: Analyze performance metrics

### Supported Data Formats

The backtester expects CSV data in [Databento](https://databento.com/) format with columns:
- `ts_event`: Timestamp (nanoseconds)
- `rtype`: Record type (32=1s, 33=1m, 34=1h, 35=1d bars)
- `open`, `high`, `low`, `close`: OHLC prices (scaled by 1e9)
- `volume`: Trading volume
- `symbol`: Instrument symbol

### Indicator Naming Convention

Indicators must follow a specific naming pattern for chart plotting:

```python
# Format: "<2-digit-number>_<indicator_name>"
self._market_data_df["00_sma_50"] = ...    # Plots on price chart
self._market_data_df["01_rsi"] = ...       # Plots in subplot 1
self._market_data_df["01_rsi_ma"] = ...    # Also plots in subplot 1
self._market_data_df["02_macd"] = ...      # Plots in subplot 2
```

- `00_*`: Overlays on the main price chart
- `01_*`, `02_*`, etc.: Groups indicators in separate subplots

## Detailed Tutorials

### Working with Market Data

#### Loading Data

```python
# Basic loading
backtester.load_historical_market_data("data.csv")

# With symbol filtering
backtester.load_historical_market_data("data.csv", symbol="MNQZ4")
```

#### Data Conversion

If your data isn't in Databento format, use the conversion helper:

```python
from aroleid_simple_strategy_prototyper.helpers import convert_csv_to_databento_format

# Convert your CSV to Databento format
convert_csv_to_databento_format("input.csv", "output_databento.csv")
```

### Contract Configuration

#### Futures Contracts

```python
# Micro E-mini NASDAQ-100
backtester.set_contract_specifications(
    symbol="MNQ", point_value=2.0, tick_size=0.25,
    broker_commission_per_contract=0.25, exchange_fees_per_contract=0.37
)

# E-mini S&P 500
backtester.set_contract_specifications(
    symbol="ES", point_value=50.0, tick_size=0.25,
    broker_commission_per_contract=0.50, exchange_fees_per_contract=1.20
)
```

#### Equity Simulation

```python
# For equity backtesting, use point_value=1 and appropriate tick_size
backtester.set_contract_specifications(
    symbol="AAPL", point_value=1.0, tick_size=0.01,
    broker_commission_per_contract=0.005, exchange_fees_per_contract=0.0
)
```

### Advanced Indicator Examples

#### Multiple Moving Averages

```python
def add_indicators(self) -> None:
    close = self._market_data_df["close"]
    
    # Multiple SMAs on price chart
    self._market_data_df["00_sma_20"] = close.rolling(20).mean()
    self._market_data_df["00_sma_50"] = close.rolling(50).mean()
    self._market_data_df["00_sma_200"] = close.rolling(200).mean()
    
    # Bollinger Bands
    sma_20 = close.rolling(20).mean()
    std_20 = close.rolling(20).std()
    self._market_data_df["00_bb_upper"] = sma_20 + (2 * std_20)
    self._market_data_df["00_bb_lower"] = sma_20 - (2 * std_20)
```

#### Momentum Indicators

```python
def add_indicators(self) -> None:
    # RSI in subplot 1
    self._market_data_df["01_rsi"] = self._calculate_rsi(14)
    self._market_data_df["01_rsi_ma"] = (
        self._market_data_df["01_rsi"].rolling(5).mean()
    )
    
    # MACD in subplot 2
    ema_12 = self._market_data_df["close"].ewm(span=12).mean()
    ema_26 = self._market_data_df["close"].ewm(span=26).mean()
    self._market_data_df["02_macd"] = ema_12 - ema_26
    self._market_data_df["02_macd_signal"] = (
        self._market_data_df["02_macd"].ewm(span=9).mean()
    )
```

## Development Status

### Current Features ✅

- ✅ Historical data loading (Databento CSV format)
- ✅ Contract specifications and fee modeling
- ✅ Technical indicator framework
- ✅ Backtesting infrastructure
- ✅ Logging and debugging support

### In Development 🚧

- 🚧 **Order execution logic** - Currently a stub in `strategy()` method
- 🚧 **Position management** - Order processing and trade execution
- 🚧 **Performance analytics** - P&L calculation and metrics
- 🚧 **Chart plotting** - Visualization of results and indicators

### Planned Features 📋

- 📋 Multiple timeframe support
- 📋 Portfolio backtesting
- 📋 Risk management tools
- 📋 Strategy optimization

> **Note**: The `strategy()` method is currently a stub. Order execution and position management are not yet implemented. The package currently supports data loading, indicator calculation, and backtesting infrastructure setup.

## Development

### Feature Roadmap

Features are tracked with numbered identifiers for Git workflow:

**Completed**:
- `#01-Github-workflow-in-README` ✅ GitHub workflow documentation
- `#02-csv-to-pandas_df` ✅ CSV data loading functionality  
- `#03-contract-specifications` ✅ Contract specification system

**In Progress**:
- `#04-order-execution-logic` 🚧 Order execution and position management

### GitHub Flow Workflow

This project follows [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow) for development:

```bash
# 1. Create feature branch
git checkout master
git pull origin master
git checkout -b feature/#04-order-execution-logic

# 2. Make changes and commit
git add .
git commit -m "Feature #04: Add market order execution"

# 3. Verify code quality
./scripts/precheck-featuremerge.sh

# 4. Merge to master
git checkout master
git merge feature/#04-order-execution-logic
git push origin master

# 5. Cleanup
git branch -d feature/#04-order-execution-logic
```

### Release Process

```bash
# Update version
poetry version patch  # or minor/major

# Build and test
poetry build
pip install dist/*.whl

# Create release
git tag -a v$(poetry version -s) -m "Release v$(poetry version -s)"
git push origin v$(poetry version -s)

# Publish
poetry publish
```

---

**Happy backtesting! 📈**
