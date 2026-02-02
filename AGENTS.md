# AGENTS.md - chanlun-pro Development Guide

## Project Overview
- **Focus**: Cryptocurrency market (Binance) analysis using 缠论 (Chan Lun) theory
- **Main Market**: CURRENCY (数字货币合约)
- **Exchange**: Binance

---

## Build / Lint / Test Commands

### Installation
```bash
# Using uv (preferred)
uv pip install -e .

# Using pip
pip install -r requirements.txt
```

### Running Tests
```bash
# Run all tests
pytest

# Run a specific test file
pytest src/chanlun/strategy/strategy_test.py

# Run a specific test class
pytest src/chanlun/strategy/strategy_test.py::StrategyTest

# Run a specific test method
pytest src/chanlun/strategy/strategy_test.py::StrategyTest::open
```

### Code Quality
No configured linters. Run basic checks manually:
```bash
# Check Python syntax
python -m py_compile src/chanlun/*.py

# Import verification
python -c "from chanlun import cl; print('Import successful')"
```

---

## Code Style Guidelines

### Imports
- Group imports: stdlib → third-party → local modules
- Sort alphabetically within each group
- Use explicit imports (`from typing import Dict, List`)
- Separate groups with blank lines

```python
import datetime
from typing import Dict, List, Union

import numpy as np
import pandas as pd

from chanlun import config, fun
from chanlun.base import Market
from chanlun.db import db
```

### Type Hints
- Required for function signatures and class attributes
- Use `Union[X, Y]` instead of `X | Y` (Python 3.11 compatibility)
- Common types: `Dict`, `List`, `Optional[Type]`, `Union[Type, None]`
- Variable annotations: `self.name: str = name`

### Naming Conventions
- **Classes**: PascalCase (`class StrategyTest:`)
- **Functions/variables**: snake_case (`def get_cl_data():`)
- **Constants**: SCREAMING_SNAKE_CASE (`MAX_RETRIES = 3`)
- **Private methods**: prefix with `_` (`def _helper_method():`)
- **Module-level private**: prefix with `g_` (`g_all_stocks = []`)

### File Structure
- Encoding: `# -*- coding: utf-8 -*-` at top of Python files
- Docstrings: Triple quotes with Chinese/English descriptions
- Line length: 120+ characters acceptable
- Blank lines: 2 between top-level definitions, 1 between method definitions

### Error Handling
- Use try/except blocks for external API calls
- Raise exceptions with descriptive messages: `raise Exception(f"message {detail}")`
- Handle None returns explicitly: `if result is None: return`
- Use tenacity for network retries:

```python
from tenacity import retry, stop_after_attempt, wait_random

@retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=5))
def fetch_data(self, code: str) -> pd.DataFrame:
    # API call logic
    pass
```

### Common Patterns
- Singleton decorator: `@fun.singleton` for exchange classes
- Abstract base classes: `from abc import ABC, abstractmethod`
- Dataclasses: `@dataclass` for simple data objects
- Logging: `from chanlun.fun import get_logger`

---

## Project Structure

### Core Modules
- **src/chanlun/**: Main package
  - `cl.py`: Core缠论 calculation (~1.4MB)
  - `cl_interface.py`: Abstract interfaces (`ICL`, `BI`, `XD`, `ZS`)
  - `cl_utils.py`: Utility functions
  - `cl_analyse.py`: Analysis tools
  - `db.py`: SQLAlchemy database models
  - `base.py`: Base enums (Market only: CURRENCY)
  - `kcharts.py`: Chart rendering
  - `monitor.py`: Monitoring system
  - `zixuan.py`: Watchlist management

### Exchange Module
- **src/chanlun/exchange/**:
  - `exchange.py`: Base Exchange class
  - `exchange_binance.py`: Binance perpetual futures
  - `exchange_db.py`: Database caching layer

### Backtesting Module
- **src/chanlun/backtesting/**:
  - `backtest.py`: Main backtesting engine
  - `base.py`: Backtesting base classes
  - `signal_to_trade.py`: Signal conversion
  - `klines_generator.py`: K-line generation

### Strategy Module
- **src/chanlun/strategy/**:
  - All strategy implementations (all preserved)

### Trader Module
- **src/chanlun/trader/**:
  - `trader_currency.py`: Live trading for crypto
  - `online_market_datas.py`: Real-time market data

---

## Database Patterns
```python
class TableByExample(Base):
    __tablename__ = "cl_example"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), comment="名称")
    __table_args__ = {"mysql_collate": "utf8mb4_general_ci"}
```

## Exchange Integration
```python
@fun.singleton
class ExchangeBinance(Exchange):
    g_all_stocks = []

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=5))
    def klines(self, code: str, frequency: str, start_date: str = None) -> pd.DataFrame:
        # Implementation
        pass
```

## Backtesting Framework
```python
class MyStrategy(Strategy):
    def open(self, code, market_data: MarketDatas, poss: Dict) -> List[Operation]:
        # Generate buy operations
        pass

    def close(self, code, mmd: str, pos: POSITION, market_data: MarketDatas) -> Operation:
        # Generate sell operations
        pass
```

## Configuration
- Global config in `chanlun/config.py`
- Data paths: `from chanlun.config import get_data_path()`
- Proxy settings: `from chanlun.utils import config_get_proxy()`
