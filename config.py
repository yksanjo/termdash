"""Configuration management for TermDash."""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

from .widget import WidgetConfig
from .dashboard import Dashboard


class ConfigManager:
    """Manage dashboard configurations."""
    
    DEFAULT_CONFIG_DIR = os.path.expanduser("~/.config/termdash")
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or self.DEFAULT_CONFIG_DIR)
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def save_dashboard(self, name: str, config: Dict[str, Any]) -> str:
        """Save a dashboard configuration."""
        filepath = self.config_dir / f"{name}.json"
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        return str(filepath)
    
    def load_dashboard(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a dashboard configuration."""
        filepath = self.config_dir / f"{name}.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def list_dashboards(self) -> List[str]:
        """List all saved dashboard names."""
        dashboards = []
        for filepath in self.config_dir.glob("*.json"):
            dashboards.append(filepath.stem)
        return sorted(dashboards)
    
    def delete_dashboard(self, name: str) -> bool:
        """Delete a dashboard configuration."""
        filepath = self.config_dir / f"{name}.json"
        
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def export_widget_config(self, widget_config: WidgetConfig) -> Dict[str, Any]:
        """Export widget config to dict."""
        return {
            "name": widget_config.name,
            "title": widget_config.title,
            "refresh_interval": widget_config.refresh_interval,
            "width": widget_config.width,
            "height": widget_config.height,
            "border_style": widget_config.border_style,
            "padding": widget_config.padding,
            "show_header": widget_config.show_header,
            "show_footer": widget_config.show_footer,
            "custom_settings": widget_config.custom_settings
        }
    
    def import_widget_config(self, data: Dict[str, Any]) -> WidgetConfig:
        """Import widget config from dict."""
        return WidgetConfig(
            name=data["name"],
            title=data.get("title", ""),
            refresh_interval=data.get("refresh_interval", 60.0),
            width=data.get("width"),
            height=data.get("height"),
            border_style=data.get("border_style", "blue"),
            padding=data.get("padding", 1),
            show_header=data.get("show_header", True),
            show_footer=data.get("show_footer", False),
            custom_settings=data.get("custom_settings", {})
        )
    
    @staticmethod
    def create_default_config(name: str = "default") -> Dict[str, Any]:
        """Create a default dashboard configuration."""
        return {
            "name": name,
            "title": "My Dashboard",
            "refresh_rate": 1.0,
            "layout": {
                "type": "grid",
                "rows": 2,
                "cols": 2
            },
            "widgets": [
                {
                    "type": "clock",
                    "config": {
                        "name": "clock",
                        "title": "🕐 Clock",
                        "refresh_interval": 1.0,
                        "border_style": "cyan"
                    },
                    "position": {"row": 0, "col": 0}
                },
                {
                    "type": "system",
                    "config": {
                        "name": "system",
                        "title": "🖥️  System",
                        "refresh_interval": 2.0,
                        "border_style": "green"
                    },
                    "position": {"row": 0, "col": 1}
                },
                {
                    "type": "todos",
                    "config": {
                        "name": "todos",
                        "title": "✅ Todos",
                        "refresh_interval": 5.0,
                        "border_style": "yellow"
                    },
                    "position": {"row": 1, "col": 0}
                },
                {
                    "type": "crypto",
                    "config": {
                        "name": "crypto",
                        "title": "₿ Crypto",
                        "refresh_interval": 30.0,
                        "border_style": "bright_yellow"
                    },
                    "position": {"row": 1, "col": 1}
                }
            ]
        }


def load_dashboard_from_config(config: Dict[str, Any]) -> Dashboard:
    """Create a dashboard from a configuration dict."""
    from .widgets import (
        ClockWidget, SystemStatsWidget, CPUMemoryWidget, 
        DiskWidget, NetworkWidget, WeatherWidget,
        StockWidget, CryptoWidget, TodoWidget,
        CountdownWidget, WorldClockWidget, LogWidget,
        QuoteWidget, SparklineWidget, BarChartWidget
    )
    
    # Create dashboard
    dashboard = Dashboard(
        title=config.get("title", "TermDash"),
        refresh_rate=config.get("refresh_rate", 1.0)
    )
    
    # Set up layout
    layout_config = config.get("layout", {"type": "grid", "rows": 2, "cols": 2})
    if layout_config["type"] == "grid":
        from .layout import GridLayout
        dashboard.layout = GridLayout(
            rows=layout_config.get("rows", 2),
            cols=layout_config.get("cols", 2)
        )
    
    # Widget factory mapping
    widget_types = {
        "clock": ClockWidget,
        "system": SystemStatsWidget,
        "cpumem": CPUMemoryWidget,
        "disk": DiskWidget,
        "network": NetworkWidget,
        "weather": WeatherWidget,
        "stock": StockWidget,
        "crypto": CryptoWidget,
        "todos": TodoWidget,
        "countdown": CountdownWidget,
        "worldclock": WorldClockWidget,
        "log": LogWidget,
        "quote": QuoteWidget,
        "sparkline": SparklineWidget,
        "barchart": BarChartWidget,
    }
    
    # Add widgets
    for widget_data in config.get("widgets", []):
        widget_type = widget_data.get("type", "")
        widget_config_data = widget_data.get("config", {})
        position = widget_data.get("position", {"row": 0, "col": 0})
        
        if widget_type in widget_types:
            widget_class = widget_types[widget_type]
            
            # Create widget config
            widget_config = WidgetConfig(
                name=widget_config_data.get("name", widget_type),
                title=widget_config_data.get("title", ""),
                refresh_interval=widget_config_data.get("refresh_interval", 60.0),
                border_style=widget_config_data.get("border_style", "blue"),
                show_header=widget_config_data.get("show_header", True),
                show_footer=widget_config_data.get("show_footer", False),
            )
            
            # Create widget
            widget = widget_class(config=widget_config)
            
            # Add to dashboard
            dashboard.add_widget(
                widget,
                row=position.get("row", 0),
                col=position.get("col", 0),
                row_span=position.get("row_span", 1),
                col_span=position.get("col_span", 1)
            )
    
    return dashboard
