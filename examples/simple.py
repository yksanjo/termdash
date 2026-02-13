#!/usr/bin/env python3
"""
Simple Dashboard Example - Minimal setup to get started.
"""

import sys
import os

# Add parent directory to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from termdash import Dashboard
from termdash.widgets import (
    ClockWidget,
    SystemStatsWidget,
    TodoWidget,
)


def main():
    """Create a simple 4-widget dashboard."""
    
    # Create dashboard
    dashboard = Dashboard(title="Simple Dashboard")
    
    # Use 2x2 grid layout
    dashboard.set_grid(rows=2, cols=2)
    
    # Add widgets
    dashboard.add_widget(ClockWidget(), row=0, col=0)
    dashboard.add_widget(SystemStatsWidget(), row=0, col=1)
    dashboard.add_widget(TodoWidget(), row=1, col=0)
    dashboard.add_widget(TodoWidget(config=None), row=1, col=1)  # Second todo list
    
    # Run
    print("Starting Simple Dashboard...")
    print("Press 'q' to quit")
    dashboard.run()


if __name__ == "__main__":
    main()
