#!/usr/bin/env python3
"""
TermDash Demo - A showcase of all available widgets.

Run this to see TermDash in action with a variety of widgets.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from termdash import Dashboard
from termdash.widgets import (
    ClockWidget,
    SystemStatsWidget,
    WeatherWidget,
    CryptoWidget,
    TodoWidget,
    QuoteWidget,
    LogWidget,
    SparklineWidget,
    CPUMemoryWidget
)


def main():
    """Create and run a demo dashboard."""
    
    # Create dashboard with 2x3 grid layout
    dashboard = Dashboard(title="🚀 TermDash Demo", refresh_rate=1.0)
    dashboard.set_grid(rows=2, cols=3)
    
    # 1. Clock widget (top-left)
    clock = ClockWidget()
    dashboard.add_widget(clock, row=0, col=0)
    
    # 2. System stats (top-middle)
    system = SystemStatsWidget()
    dashboard.add_widget(system, row=0, col=1)
    
    # 3. CPU/Memory mini widget (top-right)
    cpumem = CPUMemoryWidget()
    dashboard.add_widget(cpumem, row=0, col=2)
    
    # 4. Crypto prices (bottom-left)
    crypto = CryptoWidget(coins=["bitcoin", "ethereum", "solana"])
    dashboard.add_widget(crypto, row=1, col=0)
    
    # 5. Todo list (bottom-middle)
    todos = TodoWidget()
    # Add some example todos
    todos.add("Review TermDash code", priority="high")
    todos.add("Write documentation", priority="medium")
    todos.add("Share with friends", priority="low")
    dashboard.add_widget(todos, row=1, col=1)
    
    # 6. Quote widget (bottom-right)
    quote = QuoteWidget()
    dashboard.add_widget(quote, row=1, col=2)
    
    # Run the dashboard
    print("Starting TermDash Demo...")
    print("Press 'q' to quit, 'r' to refresh, 'h' for help")
    
    try:
        dashboard.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
