#!/usr/bin/env python3
"""
System Monitor Dashboard - Focus on system statistics.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from termdash import Dashboard
from termdash.widgets import (
    ClockWidget,
    SystemStatsWidget,
    CPUMemoryWidget,
    DiskWidget,
    NetworkWidget,
    LogWidget
)


def main():
    """Create and run a system monitoring dashboard."""
    
    # Create dashboard with custom layout
    dashboard = Dashboard(title="🖥️  System Monitor", refresh_rate=1.0)
    dashboard.set_grid(rows=3, cols=2)
    
    # Row 1: Clock and main system stats
    clock = ClockWidget()
    dashboard.add_widget(clock, row=0, col=0)
    
    system = SystemStatsWidget()
    dashboard.add_widget(system, row=0, col=1, row_span=2)
    
    # Row 2: CPU/Memory chart and Network
    cpumem = CPUMemoryWidget()
    dashboard.add_widget(cpumem, row=1, col=0)
    
    network = NetworkWidget()
    dashboard.add_widget(network, row=2, col=0)
    
    # Row 3: Disk usage spanning both columns
    disk = DiskWidget(paths=["/", "/home"] if os.path.exists("/home") else ["/"])
    dashboard.add_widget(disk, row=2, col=1)
    
    # Run
    print("Starting System Monitor...")
    dashboard.run()


if __name__ == "__main__":
    main()
