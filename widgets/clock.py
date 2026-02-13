"""Clock and time-related widgets."""

from datetime import datetime, timedelta
from typing import Optional, List
from collections import deque

from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align

from ..widget import Widget, WidgetConfig


class ClockWidget(Widget):
    """Digital clock widget."""
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 timezone: Optional[str] = None,
                 show_seconds: bool = True,
                 format_24h: bool = True):
        if config is None:
            config = WidgetConfig(
                name="clock",
                title="🕐 Clock",
                refresh_interval=1.0,
                border_style="bright_cyan"
            )
        super().__init__(config)
        self.timezone = timezone
        self.show_seconds = show_seconds
        self.format_24h = format_24h
    
    async def fetch_data(self) -> dict:
        """Get current time."""
        now = datetime.now()
        
        return {
            "time": now,
            "day": now.strftime("%A"),
            "date": now.strftime("%B %d, %Y"),
            "week": now.isocalendar()[1],
        }
    
    def render(self) -> Panel:
        """Render clock."""
        if not self.data:
            return Panel("Loading...", title=self.config.title,
                        border_style=self.config.border_style)
        
        d = self.data
        now = d["time"]
        
        # Format time
        if self.format_24h:
            time_str = now.strftime("%H:%M:%S" if self.show_seconds else "%H:%M")
        else:
            time_str = now.strftime("%I:%M:%S %p" if self.show_seconds else "%I:%M %p")
        
        # Create big clock display
        time_text = Text(time_str, style="bold bright_cyan", justify="center")
        time_text.stylize("bold", 0, len(time_str))
        
        # Date and day
        info = Table.grid(expand=True)
        info.add_column(justify="center")
        info.add_row(Text(d["day"], style="yellow"))
        info.add_row(Text(d["date"], style="dim"))
        
        content = Table.grid(expand=True)
        content.add_column(justify="center")
        content.add_row("")
        content.add_row(time_text)
        content.add_row("")
        content.add_row(info)
        
        return Panel(
            content,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style
        )


class CountdownWidget(Widget):
    """Countdown timer widget."""
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 target: Optional[datetime] = None,
                 title_text: Optional[str] = None):
        if config is None:
            config = WidgetConfig(
                name="countdown",
                title="⏱️  Countdown",
                refresh_interval=1.0,
                border_style="bright_yellow"
            )
        super().__init__(config)
        self.target = target or (datetime.now() + timedelta(hours=1))
        self.title_text = title_text or "Time Remaining"
    
    def set_target(self, target: datetime) -> None:
        """Set a new target datetime."""
        self.target = target
    
    def set_duration(self, hours: int = 0, minutes: int = 0, seconds: int = 0) -> None:
        """Set target as duration from now."""
        self.target = datetime.now() + timedelta(
            hours=hours, minutes=minutes, seconds=seconds
        )
    
    async def fetch_data(self) -> dict:
        """Calculate time remaining."""
        now = datetime.now()
        remaining = self.target - now
        
        total_seconds = max(0, int(remaining.total_seconds()))
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": total_seconds,
            "expired": remaining.total_seconds() <= 0
        }
    
    def render(self) -> Panel:
        """Render countdown."""
        if not self.data:
            return Panel("Loading...", title=self.config.title,
                        border_style=self.config.border_style)
        
        d = self.data
        
        if d["expired"]:
            time_display = Text("TIME'S UP!", style="bold red blink", justify="center")
        else:
            # Build time string
            parts = []
            if d["days"] > 0:
                parts.append(f"{d['days']}d")
            parts.append(f"{d['hours']:02d}h")
            parts.append(f"{d['minutes']:02d}m")
            parts.append(f"{d['seconds']:02d}s")
            
            time_str = " ".join(parts)
            time_display = Text(time_str, style="bold bright_yellow", justify="center")
        
        content = Table.grid(expand=True)
        content.add_column(justify="center")
        content.add_row("")
        content.add_row(Text(self.title_text, style="dim", justify="center"))
        content.add_row("")
        content.add_row(time_display)
        content.add_row("")
        
        border_style = "red" if d["expired"] else self.config.border_style
        
        return Panel(
            content,
            title=self.config.title if self.config.show_header else None,
            border_style=border_style
        )


class WorldClockWidget(Widget):
    """Multiple timezone clock widget."""
    
    ZONES = {
        "UTC": 0,
        "London": 0,
        "Paris": 1,
        "Berlin": 1,
        "Tokyo": 9,
        "Sydney": 11,
        "New York": -5,
        "Los Angeles": -8,
    }
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 cities: Optional[List[str]] = None):
        if config is None:
            config = WidgetConfig(
                name="worldclock",
                title="🌍 World Clock",
                refresh_interval=60.0,
                border_style="cyan"
            )
        super().__init__(config)
        self.cities = cities or ["UTC", "London", "Tokyo", "New York"]
    
    async def fetch_data(self) -> List[dict]:
        """Get times for all cities."""
        now = datetime.utcnow()
        results = []
        
        for city in self.cities:
            offset = self.ZONES.get(city, 0)
            city_time = now + timedelta(hours=offset)
            
            results.append({
                "city": city,
                "time": city_time.strftime("%H:%M"),
                "date": city_time.strftime("%a %d"),
                "offset": f"UTC{'+' if offset >= 0 else ''}{offset}"
            })
        
        return results
    
    def render(self) -> Panel:
        """Render world clock."""
        if not self.data:
            return Panel("Loading...", title=self.config.title,
                        border_style=self.config.border_style)
        
        table = Table(expand=True, box=None, show_header=False)
        table.add_column("City", style="cyan")
        table.add_column("Time", style="bright_yellow", justify="right")
        table.add_column("Date", style="dim", justify="right")
        
        for city_data in self.data:
            table.add_row(
                city_data["city"],
                city_data["time"],
                city_data["date"]
            )
        
        return Panel(
            table,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style
        )
