#!/usr/bin/env python3
"""
TermDash - Command Line Interface

Usage:
    python -m termdash                    # Run default dashboard
    python -m termdash demo               # Run demo dashboard
    python -m termdash system             # Run system monitor
    python -m termdash finance            # Run finance dashboard
    python -m termdash load <name>        # Load saved dashboard
    python -m termdash save <name>        # Save current as default
    python -m termdash list               # List saved dashboards
"""

import sys
import argparse

from .config import ConfigManager, load_dashboard_from_config
from .dashboard import Dashboard


def create_default_dashboard() -> Dashboard:
    """Create the default dashboard."""
    from .widgets import (
        ClockWidget,
        SystemStatsWidget,
        CryptoWidget,
        TodoWidget
    )
    
    dashboard = Dashboard(title="🚀 TermDash", refresh_rate=1.0)
    dashboard.set_grid(rows=2, cols=2)
    
    dashboard.add_widget(ClockWidget(), row=0, col=0)
    dashboard.add_widget(SystemStatsWidget(), row=0, col=1)
    dashboard.add_widget(TodoWidget(), row=1, col=0)
    dashboard.add_widget(CryptoWidget(), row=1, col=1)
    
    return dashboard


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="TermDash - Customizable Terminal Dashboards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m termdash                    # Run default dashboard
    python -m termdash demo               # Run demo with all widgets
    python -m termdash system             # Run system monitor
    python -m termdash finance            # Run finance dashboard
    python -m termdash load mydash        # Load saved dashboard
    python -m termdash list               # List saved dashboards
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        default="default",
        help="Command or dashboard to run (default: default)"
    )
    parser.add_argument(
        "name",
        nargs="?",
        help="Dashboard name for load/save commands"
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.command == "list":
        config_mgr = ConfigManager()
        dashboards = config_mgr.list_dashboards()
        if dashboards:
            print("Saved dashboards:")
            for name in dashboards:
                print(f"  - {name}")
        else:
            print("No saved dashboards.")
        return
    
    if args.command == "save":
        if not args.name:
            print("Error: Please provide a name for the dashboard")
            return
        config_mgr = ConfigManager()
        config = ConfigManager.create_default_config(args.name)
        filepath = config_mgr.save_dashboard(args.name, config)
        print(f"Dashboard saved to: {filepath}")
        return
    
    # Determine which dashboard to run
    dashboard = None
    
    if args.command == "demo":
        from .examples.demo import main as demo_main
        demo_main()
        return
    
    elif args.command == "system":
        from .examples.system_monitor import main as system_main
        system_main()
        return
    
    elif args.command == "finance":
        from .examples.finance_dashboard import main as finance_main
        finance_main()
        return
    
    elif args.command == "load":
        if not args.name:
            print("Error: Please provide a dashboard name to load")
            return
        config_mgr = ConfigManager()
        config = config_mgr.load_dashboard(args.name)
        if config:
            dashboard = load_dashboard_from_config(config)
        else:
            print(f"Dashboard '{args.name}' not found.")
            return
    
    else:
        # Try to load named dashboard or use default
        config_mgr = ConfigManager()
        config = config_mgr.load_dashboard(args.command)
        if config:
            dashboard = load_dashboard_from_config(config)
        else:
            dashboard = create_default_dashboard()
    
    # Run the dashboard
    if dashboard:
        try:
            print(f"Starting {dashboard.title}...")
            print("Press 'q' to quit, 'r' to refresh, 'h' for help")
            dashboard.run()
        except KeyboardInterrupt:
            print("\nGoodbye!")


if __name__ == "__main__":
    main()
