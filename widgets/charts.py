"""Chart and graph widgets for TermDash."""

from typing import Optional, List, Dict, Any, Callable
from collections import deque
from datetime import datetime

from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.console import Group
from rich.align import Align

from ..widget import Widget, WidgetConfig


class SparklineWidget(Widget):
    """Widget displaying a sparkline chart."""
    
    BLOCKS = "▁▂▃▄▅▆▇█"
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 data: Optional[List[float]] = None,
                 max_points: int = 50,
                 data_provider: Optional[Callable[[], float]] = None,
                 min_value: Optional[float] = None,
                 max_value: Optional[float] = None,
                 label: str = "Value"):
        if config is None:
            config = WidgetConfig(
                name="sparkline",
                title="📊 Sparkline",
                refresh_interval=2.0,
                border_style="cyan"
            )
        super().__init__(config)
        self.max_points = max_points
        self.data_provider = data_provider
        self.history: deque[float] = deque(maxlen=max_points)
        self.min_value = min_value
        self.max_value = max_value
        self.label = label
        
        if data:
            self.history.extend(data[-max_points:])
    
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch new data point."""
        if self.data_provider:
            try:
                value = self.data_provider()
                self.history.append(value)
            except Exception as e:
                pass
        
        values = list(self.history)
        if not values:
            return {"values": [], "min": 0, "max": 0, "current": 0, "avg": 0}
        
        min_val = self.min_value if self.min_value is not None else min(values)
        max_val = self.max_value if self.max_value is not None else max(values)
        
        return {
            "values": values,
            "min": min_val,
            "max": max_val,
            "current": values[-1] if values else 0,
            "avg": sum(values) / len(values) if values else 0,
            "range": max_val - min_val if max_val != min_val else 1
        }
    
    def render(self) -> Panel:
        """Render sparkline."""
        if not self.data or not self.data["values"]:
            return Panel("No data", title=self.config.title,
                        border_style=self.config.border_style)
        
        d = self.data
        values = d["values"]
        
        # Create sparkline
        spark = ""
        min_val, max_val = d["min"], d["max"]
        range_val = max_val - min_val if max_val != min_val else 1
        
        for val in values:
            idx = int(((val - min_val) / range_val) * (len(self.BLOCKS) - 1))
            idx = max(0, min(idx, len(self.BLOCKS) - 1))
            spark += self.BLOCKS[idx]
        
        # Stats
        stats = Table.grid(expand=True)
        stats.add_column(style="dim")
        stats.add_column(style="green")
        stats.add_column(style="dim")
        stats.add_column(style="yellow")
        stats.add_column(style="dim")
        stats.add_column(style="cyan")
        
        stats.add_row(
            "Current:", f"{d['current']:.2f}",
            "Avg:", f"{d['avg']:.2f}",
            "Range:", f"{min_val:.2f} - {max_val:.2f}"
        )
        
        content = Group(
            Text(spark, style="bright_cyan"),
            Text(""),
            stats
        )
        
        return Panel(
            content,
            title=f"{self.config.title} - {self.label}" if self.config.show_header else None,
            border_style=self.config.border_style
        )
    
    def add_value(self, value: float) -> None:
        """Add a value to the history."""
        self.history.append(value)


class BarChartWidget(Widget):
    """Widget displaying a bar chart."""
    
    BARS = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 data: Optional[Dict[str, float]] = None,
                 data_provider: Optional[Callable[[], Dict[str, float]]] = None,
                 max_bar_width: int = 20,
                 horizontal: bool = True):
        if config is None:
            config = WidgetConfig(
                name="barchart",
                title="📊 Bar Chart",
                refresh_interval=5.0,
                border_style="green"
            )
        super().__init__(config)
        self.data_dict = data or {}
        self.data_provider = data_provider
        self.max_bar_width = max_bar_width
        self.horizontal = horizontal
    
    async def fetch_data(self) -> Dict[str, float]:
        """Fetch chart data."""
        if self.data_provider:
            try:
                self.data_dict = self.data_provider()
            except Exception:
                pass
        
        return self.data_dict
    
    def render(self) -> Panel:
        """Render bar chart."""
        if not self.data:
            return Panel("No data", title=self.config.title,
                        border_style=self.config.border_style)
        
        data = self.data
        if not data:
            return Panel("Empty", title=self.config.title,
                        border_style=self.config.border_style)
        
        max_val = max(data.values()) if data else 1
        max_label_len = max(len(str(k)) for k in data.keys()) if data else 0
        
        table = Table(expand=True, box=None, show_header=False)
        table.add_column(width=max_label_len + 2)
        table.add_column()
        table.add_column(width=10, justify="right")
        
        for label, value in data.items():
            # Calculate bar length
            ratio = value / max_val if max_val > 0 else 0
            full_blocks = int(ratio * self.max_bar_width)
            remainder = (ratio * self.max_bar_width) - full_blocks
            
            # Build bar
            bar = "█" * full_blocks
            if remainder > 0 and full_blocks < self.max_bar_width:
                idx = int(remainder * (len(self.BARS) - 1))
                bar += self.BARS[idx]
            
            # Color based on ratio
            color = "green" if ratio < 0.5 else "yellow" if ratio < 0.8 else "red"
            
            table.add_row(
                str(label),
                Text(bar, style=color),
                f"{value:.1f}"
            )
        
        return Panel(
            table,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style
        )


class GaugeWidget(Widget):
    """Widget displaying a gauge/meter."""
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 value: float = 0.0,
                 max_value: float = 100.0,
                 data_provider: Optional[Callable[[], float]] = None,
                 label: str = "Value"):
        if config is None:
            config = WidgetConfig(
                name="gauge",
                title="🎚️  Gauge",
                refresh_interval=2.0,
                border_style="yellow"
            )
        super().__init__(config)
        self.value = value
        self.max_value = max_value
        self.data_provider = data_provider
        self.label = label
    
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch gauge value."""
        if self.data_provider:
            try:
                self.value = self.data_provider()
            except Exception:
                pass
        
        ratio = self.value / self.max_value if self.max_value > 0 else 0
        ratio = max(0, min(1, ratio))  # Clamp to 0-1
        
        return {
            "value": self.value,
            "max": self.max_value,
            "ratio": ratio,
            "percent": ratio * 100
        }
    
    def render(self) -> Panel:
        """Render gauge."""
        if not self.data:
            return Panel("No data", title=self.config.title,
                        border_style=self.config.border_style)
        
        d = self.data
        ratio = d["ratio"]
        
        # Create gauge bar
        width = 30
        filled = int(ratio * width)
        
        color = "green" if ratio < 0.5 else "yellow" if ratio < 0.8 else "red"
        
        bar_left = "█" * filled
        bar_right = "░" * (width - filled)
        
        gauge = Text()
        gauge.append("[", style="dim")
        gauge.append(bar_left, style=color)
        gauge.append(bar_right, style="dim")
        gauge.append("]", style="dim")
        
        # Value display
        value_text = Text(f"{d['value']:.1f} / {d['max']:.1f} ({d['percent']:.1f}%)", 
                         style="bold", justify="center")
        
        content = Group(
            Text(""),
            Align.center(gauge),
            Text(""),
            Align.center(value_text),
            Text("")
        )
        
        return Panel(
            content,
            title=f"{self.config.title} - {self.label}" if self.config.show_header else None,
            border_style=color if ratio > 0.8 else self.config.border_style
        )


class PieChartWidget(Widget):
    """Simple ASCII pie chart widget."""
    
    SLICES = ["◔", "◑", "◕", "●"]
    COLORS = ["red", "green", "blue", "yellow", "magenta", "cyan", "white"]
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 data: Optional[Dict[str, float]] = None):
        if config is None:
            config = WidgetConfig(
                name="piechart",
                title="🥧 Distribution",
                refresh_interval=60.0,
                border_style="magenta"
            )
        super().__init__(config)
        self.data_dict = data or {}
    
    async def fetch_data(self) -> Dict[str, float]:
        return self.data_dict
    
    def render(self) -> Panel:
        """Render pie chart as list with percentages."""
        if not self.data:
            return Panel("No data", title=self.config.title,
                        border_style=self.config.border_style)
        
        data = self.data
        total = sum(data.values())
        
        if total == 0:
            return Panel("Empty", title=self.config.title,
                        border_style=self.config.border_style)
        
        table = Table(expand=True, box=None, show_header=False)
        table.add_column(width=3)
        table.add_column()
        table.add_column(width=10, justify="right")
        
        for i, (label, value) in enumerate(data.items()):
            percent = (value / total) * 100
            color = self.COLORS[i % len(self.COLORS)]
            icon = self.SLICES[min(int(percent / 25), 3)]
            
            table.add_row(
                Text(icon, style=color),
                label,
                f"{percent:.1f}%"
            )
        
        return Panel(
            table,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style
        )
