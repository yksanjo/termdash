"""Base widget class and configuration for TermDash."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import asyncio


@dataclass
class WidgetConfig:
    """Configuration for a widget."""
    name: str
    title: str = ""
    refresh_interval: float = 60.0  # seconds
    width: Optional[int] = None
    height: Optional[int] = None
    border_style: str = "blue"
    padding: int = 1
    show_header: bool = True
    show_footer: bool = False
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class Widget(ABC):
    """Base class for all dashboard widgets."""
    
    def __init__(self, config: WidgetConfig):
        self.config = config
        self.last_update: Optional[datetime] = None
        self.data: Any = None
        self.error: Optional[str] = None
        self._update_callbacks: list[Callable] = []
        self._running = False
        
    @abstractmethod
    async def fetch_data(self) -> Any:
        """Fetch data for the widget. Override in subclasses."""
        pass
    
    @abstractmethod
    def render(self) -> "Panel":
        """Render the widget as a Rich Panel. Override in subclasses."""
        from rich.panel import Panel
        from rich.text import Text
        
        if self.error:
            return Panel(
                Text(self.error, style="red"),
                title=self.config.title or self.config.name,
                border_style="red"
            )
        return Panel(
            Text("No data"),
            title=self.config.title or self.config.name,
            border_style=self.config.border_style
        )
    
    async def update(self) -> None:
        """Update widget data."""
        try:
            self.data = await self.fetch_data()
            self.error = None
            self.last_update = datetime.now()
            
            # Notify callbacks
            for callback in self._update_callbacks:
                try:
                    callback(self)
                except Exception:
                    pass
                    
        except Exception as e:
            self.error = str(e)
    
    def add_update_callback(self, callback: Callable) -> None:
        """Add a callback to be called when widget updates."""
        self._update_callbacks.append(callback)
    
    def remove_update_callback(self, callback: Callable) -> None:
        """Remove an update callback."""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)
    
    async def start_auto_update(self) -> None:
        """Start automatic updates."""
        self._running = True
        while self._running:
            await self.update()
            await asyncio.sleep(self.config.refresh_interval)
    
    def stop_auto_update(self) -> None:
        """Stop automatic updates."""
        self._running = False
    
    def get_footer_text(self) -> str:
        """Get footer text showing last update time."""
        if self.last_update:
            return f"Updated: {self.last_update.strftime('%H:%M:%S')}"
        return "Never updated"
    
    def format_value(self, value: Any, unit: str = "") -> str:
        """Helper to format values with units."""
        if value is None:
            return "N/A"
        if unit:
            return f"{value} {unit}"
        return str(value)
    
    def colorize_change(self, value: float, prefix: str = "") -> str:
        """Colorize a numeric change (green for positive, red for negative)."""
        from rich.text import Text
        
        if value > 0:
            return Text(f"{prefix}+{value:.2f}", style="green bold")
        elif value < 0:
            return Text(f"{prefix}{value:.2f}", style="red bold")
        else:
            return Text(f"{prefix}{value:.2f}", style="dim")


class TextWidget(Widget):
    """Simple text widget for static or dynamic content."""
    
    def __init__(self, config: WidgetConfig, text: str = "", 
                 content_getter: Optional[Callable] = None):
        super().__init__(config)
        self.text = text
        self.content_getter = content_getter
    
    async def fetch_data(self) -> Any:
        if self.content_getter:
            return self.content_getter()
        return self.text
    
    def render(self) -> "Panel":
        from rich.panel import Panel
        from rich.text import Text
        
        content = self.data if self.data is not None else self.text
        
        footer = None
        if self.config.show_footer:
            footer = self.get_footer_text()
        
        return Panel(
            Text(content),
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style,
            padding=(self.config.padding, self.config.padding),
            subtitle=footer
        )
