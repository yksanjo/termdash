"""Weather widget for TermDash."""

import os
import json
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any
from datetime import datetime

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Group

from ..widget import Widget, WidgetConfig


class WeatherWidget(Widget):
    """Widget displaying weather information."""
    
    # Weather condition icons
    ICONS = {
        "clear sky": "☀️",
        "few clouds": "🌤️",
        "scattered clouds": "⛅",
        "broken clouds": "☁️",
        "shower rain": "🌦️",
        "rain": "🌧️",
        "thunderstorm": "⛈️",
        "snow": "🌨️",
        "mist": "🌫️",
        "default": "🌡️"
    }
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 city: str = "London",
                 api_key: Optional[str] = None,
                 units: str = "metric"):
        if config is None:
            config = WidgetConfig(
                name="weather",
                title="🌤️  Weather",
                refresh_interval=600.0,  # 10 minutes
                border_style="bright_blue"
            )
        super().__init__(config)
        self.city = city
        self.api_key = api_key or os.environ.get("OPENWEATHER_API_KEY")
        self.units = units  # metric, imperial, or kelvin
        self._fallback_mode = self.api_key is None
    
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch weather data from OpenWeatherMap API."""
        if self._fallback_mode:
            return self._get_fallback_data()
        
        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"q={urllib.parse.quote(self.city)}&"
                f"appid={self.api_key}&"
                f"units={self.units}"
            )
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "main": data["weather"][0]["main"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 0),
                "sunrise": data["sys"]["sunrise"],
                "sunset": data["sys"]["sunset"],
                "success": True
            }
            
        except Exception as e:
            self._fallback_mode = True
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Return placeholder data when API is not available."""
        import random
        
        # Generate somewhat realistic placeholder data
        conditions = ["clear sky", "few clouds", "scattered clouds", "light rain"]
        condition = random.choice(conditions)
        
        return {
            "city": self.city,
            "country": "??",
            "temp": 20 + random.randint(-5, 10),
            "feels_like": 20 + random.randint(-5, 10),
            "humidity": 50 + random.randint(-20, 30),
            "pressure": 1013 + random.randint(-20, 20),
            "description": condition,
            "main": condition.title(),
            "wind_speed": 5 + random.randint(0, 10),
            "visibility": 10000,
            "sunrise": 0,
            "sunset": 0,
            "success": False,
            "note": "API key required for live data"
        }
    
    def render(self) -> Panel:
        """Render weather widget."""
        if not self.data:
            return Panel("Loading...", title=self.config.title,
                        border_style=self.config.border_style)
        
        d = self.data
        
        # Get weather icon
        icon = self.ICONS.get(d["description"], self.ICONS["default"])
        
        # Temperature unit symbol
        unit_symbol = "°C" if self.units == "metric" else "°F" if self.units == "imperial" else "K"
        
        # Main content
        main_table = Table.grid(expand=True)
        main_table.add_column()
        main_table.add_column(justify="right")
        
        temp_str = f"{d['temp']:.1f}{unit_symbol}"
        feels_str = f"Feels like {d['feels_like']:.1f}{unit_symbol}"
        
        main_table.add_row(
            Text(f"{icon} {d['city']}, {d['country']}", style="bold cyan"),
            Text(temp_str, style="bold yellow")
        )
        main_table.add_row(
            Text(d["description"].title(), style="dim"),
            Text(feels_str, style="dim")
        )
        
        # Details table
        details = Table.grid(expand=True)
        details.add_column(style="dim")
        details.add_column()
        details.add_column(style="dim")
        details.add_column()
        
        details.add_row(
            "💧 Humidity", f"{d['humidity']}%",
            "💨 Wind", f"{d['wind_speed']} m/s"
        )
        details.add_row(
            "📊 Pressure", f"{d['pressure']} hPa",
            "👁️  Visibility", f"{d['visibility']/1000:.1f} km"
        )
        
        # Combine
        content = Group(main_table, Text(""), details)
        
        footer = None
        if not d.get("success"):
            footer = Text("Demo mode - Add OPENWEATHER_API_KEY", style="dim yellow")
        elif self.config.show_footer:
            footer = self.get_footer_text()
        
        return Panel(
            content,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style,
            padding=(self.config.padding, self.config.padding),
            subtitle=footer
        )
