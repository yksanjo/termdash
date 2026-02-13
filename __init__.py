"""
TermDash - A customizable terminal dashboard builder.

Create beautiful terminal dashboards with widgets for stocks, weather, 
todos, system stats, and more.
"""

__version__ = "1.0.0"
__author__ = "TermDash"

from .dashboard import Dashboard
from .widget import Widget, WidgetConfig
from .layout import Layout, GridLayout

__all__ = ["Dashboard", "Widget", "WidgetConfig", "Layout", "GridLayout"]
