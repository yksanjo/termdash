"""Built-in widgets for TermDash."""

from .system import SystemStatsWidget, CPUMemoryWidget, DiskWidget, NetworkWidget
from .weather import WeatherWidget
from .stocks import StockWidget, CryptoWidget
from .todos import TodoWidget
from .clock import ClockWidget, CountdownWidget
from .text import LogWidget, QuoteWidget
from .charts import SparklineWidget, BarChartWidget

__all__ = [
    "SystemStatsWidget",
    "CPUMemoryWidget", 
    "DiskWidget",
    "NetworkWidget",
    "WeatherWidget",
    "StockWidget",
    "CryptoWidget",
    "TodoWidget",
    "ClockWidget",
    "CountdownWidget",
    "LogWidget",
    "QuoteWidget",
    "SparklineWidget",
    "BarChartWidget",
]
