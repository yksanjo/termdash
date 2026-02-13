#!/usr/bin/env python3
"""
Finance Dashboard - Stock prices, crypto, and market data.
"""

import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from termdash import Dashboard
from termdash.widgets import (
    ClockWidget,
    StockWidget,
    CryptoWidget,
    SparklineWidget,
    BarChartWidget,
    QuoteWidget
)


def main():
    """Create and run a finance dashboard."""
    
    dashboard = Dashboard(title="💰 Finance Dashboard", refresh_rate=2.0)
    dashboard.set_grid(rows=2, cols=3)
    
    # Clock
    clock = ClockWidget()
    dashboard.add_widget(clock, row=0, col=0)
    
    # Stock prices
    stocks = StockWidget(symbols=["AAPL", "GOOGL", "MSFT", "TSLA"])
    dashboard.add_widget(stocks, row=0, col=1)
    
    # Crypto prices
    crypto = CryptoWidget(coins=["bitcoin", "ethereum", "solana", "cardano"])
    dashboard.add_widget(crypto, row=0, col=2)
    
    # Portfolio sparkline (demo data)
    def portfolio_value():
        # Simulate portfolio value changes
        return 50000 + random.gauss(0, 500)
    
    portfolio = SparklineWidget(
        data=[50000 + random.gauss(0, 500) for _ in range(30)],
        data_provider=portfolio_value,
        label="Portfolio Value",
        max_points=50
    )
    dashboard.add_widget(portfolio, row=1, col=0)
    
    # Asset allocation bar chart
    allocation_data = {
        "Stocks": 45,
        "Crypto": 25,
        "Bonds": 20,
        "Cash": 10
    }
    
    def get_allocation():
        # Slightly vary the allocation
        base = {"Stocks": 45, "Crypto": 25, "Bonds": 20, "Cash": 10}
        return {k: v + random.gauss(0, 1) for k, v in base.items()}
    
    allocation = BarChartWidget(
        data=allocation_data,
        data_provider=get_allocation
    )
    dashboard.add_widget(allocation, row=1, col=1)
    
    # Market quote
    quote = QuoteWidget(
        quotes=[
            "Price is what you pay. Value is what you get. - Warren Buffett",
            "The stock market is a device for transferring money from the impatient to the patient. - Warren Buffett",
            "In investing, what is comfortable is rarely profitable. - Robert Arnott",
            "The four most dangerous words in investing are: 'This time it's different.' - John Templeton",
            "Compound interest is the eighth wonder of the world. - Albert Einstein",
        ],
        rotate_interval=3
    )
    dashboard.add_widget(quote, row=1, col=2)
    
    # Run
    print("Starting Finance Dashboard...")
    dashboard.run()


if __name__ == "__main__":
    main()
