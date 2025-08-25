# Algorithmic-Trading-Backtest-Engine
An independent project which delves into the mechanics of algorithmic trading and backtesting. Python-based engine designed to quantitatively assess trading strategies against a Buy & Hold benchmark using 20 years of S&amp;P500 close price data. Calculation of key risk-return metrics uncovered the real-world trade-off between risk mitigation and return maximisation.

## 🔍 Key Findings

Backtesting a 50/200-day SMA Crossover strategy revealed:
- **Nearly Identical Returns:** ~8.5% annualized returns for both SMA and Buy & Hold.
- **Marginally Superior Risk-Adjusted Performance:** Achieved a higher **Sharpe Ratio (0.451 vs. 0.445)**.
- **Significant Risk Reduction:** Demonstrated a **6% improvement in Maximum Drawdown**, highlighting effective capital preservation.

## 🔧Key Features 
- Historical data processing using `yfinance' API
- Strategy simulation (50/200-day SMA Crossover & Buy & Hold)
- Performance metrics calculation (CAGR, Sharpe Ratio, Max Drawdown)
- Equity curve visualization with `matplotlib`

## 📊 Full Report

For complete methodology and analysis, please read the full project report:

[**📄 Full Project Report (PDF)**](/Backtest_Engine_Report.pdf)
