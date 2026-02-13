# 🚀 TermDash

A customizable terminal dashboard builder with beautiful widgets for stocks, weather, todos, system stats, and more.

![TermDash Demo](https://via.placeholder.com/800x400.png?text=TermDash+Demo)

## ✨ Features

- 📊 **Built-in Widgets**: Clock, system stats, weather, stocks, crypto, todos, charts, and more
- 🎨 **Customizable**: Full control over colors, layouts, refresh rates
- ⚡ **Live Updates**: All widgets auto-update with configurable intervals
- 🎯 **Easy to Use**: Simple Python API for creating dashboards
- 🔌 **Extensible**: Create your own custom widgets
- 💾 **Persistent**: Save and load dashboard configurations

## 📦 Installation

```bash
# Clone or download the termdash folder
cd termdash

# Install dependencies
pip install -r requirements.txt

# Or install directly
pip install rich psutil
```

## 🚀 Quick Start

```bash
# Run the default dashboard
python -m termdash

# Run demo with all widgets
python -m termdash demo

# Run system monitor
python -m termdash system

# Run finance dashboard
python -m termdash finance
```

## 📖 Usage

### Basic Dashboard

```python
from termdash import Dashboard
from termdash.widgets import ClockWidget, SystemStatsWidget, TodoWidget

# Create dashboard
dashboard = Dashboard(title="My Dashboard")
dashboard.set_grid(rows=2, cols=2)

# Add widgets
dashboard.add_widget(ClockWidget(), row=0, col=0)
dashboard.add_widget(SystemStatsWidget(), row=0, col=1)
dashboard.add_widget(TodoWidget(), row=1, col=0)

# Run
dashboard.run()
```

### Custom Widget

```python
from termdash.widget import Widget, WidgetConfig
from rich.panel import Panel
from rich.text import Text

class MyWidget(Widget):
    async def fetch_data(self):
        # Fetch your data here
        return {"value": 42}
    
    def render(self):
        # Return a Rich Panel
        return Panel(
            Text(f"Value: {self.data['value']}"),
            title="My Widget",
            border_style="green"
        )

# Use it
dashboard.add_widget(MyWidget())
```

## 📊 Available Widgets

### System & Performance
| Widget | Description |
|--------|-------------|
| `SystemStatsWidget` | CPU, memory, disk, uptime |
| `CPUMemoryWidget` | Compact CPU/memory with sparklines |
| `DiskWidget` | Disk usage for multiple paths |
| `NetworkWidget` | Network I/O and connections |

### Time
| Widget | Description |
|--------|-------------|
| `ClockWidget` | Digital clock with date |
| `CountdownWidget` | Countdown timer |
| `WorldClockWidget` | Multiple timezones |

### Finance
| Widget | Description |
|--------|-------------|
| `StockWidget` | Stock prices with sparklines |
| `CryptoWidget` | Crypto prices from CoinGecko |

### Productivity
| Widget | Description |
|--------|-------------|
| `TodoWidget` | Interactive todo list (persistent) |
| `LogWidget` | Real-time log tail |
| `QuoteWidget` | Rotating quotes |

### Data Visualization
| Widget | Description |
|--------|-------------|
| `SparklineWidget` | Mini line charts |
| `BarChartWidget` | Horizontal bar charts |
| `GaugeWidget` | Progress/meter display |

### Other
| Widget | Description |
|--------|-------------|
| `WeatherWidget` | Weather info (requires API key) |
| `CodeWidget` | Syntax-highlighted code |

## 🎮 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit dashboard |
| `r` | Refresh all widgets |
| `h` | Show help |

## 📐 Layouts

### Grid Layout
```python
from termdash import GridLayout

layout = GridLayout(rows=3, cols=3)
dashboard.set_layout(layout)

# Add widgets with positioning
dashboard.add_widget(widget, row=0, col=0, row_span=2, col_span=1)
```

### Flex Layout
```python
from termdash.layout import FlexLayout

layout = FlexLayout(direction="row")
layout.add_widget(widget1, flex=2)  # Takes 2/3 space
layout.add_widget(widget2, flex=1)  # Takes 1/3 space
```

### Split Layout
```python
from termdash.layout import SplitLayout

layout = SplitLayout(split_ratio=0.7, vertical=False)
layout.set_primary(widget1)
layout.set_secondary(widget2)
```

## 💾 Configuration

### Save/Load Dashboards

```bash
# Save current configuration
python -m termdash save mydashboard

# Load saved dashboard
python -m termdash load mydashboard

# List saved dashboards
python -m termdash list
```

### Config File Format

```json
{
  "name": "mydashboard",
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
    }
  ]
}
```

## 🔌 API Keys (Optional)

Some widgets work better with API keys:

### Weather Widget
```bash
export OPENWEATHER_API_KEY="your_key_here"
```

### Stock Widget
```bash
export ALPHA_VANTAGE_API_KEY="your_key_here"
```

Without API keys, widgets show demo data.

## 🛠️ Advanced Examples

### Todo List Programmatically

```python
from termdash.widgets import TodoWidget

todos = TodoWidget()

# Add items
todos.add("Buy groceries", priority="high")
todos.add("Walk the dog", priority="medium", tags=["personal"])

# Mark done
todos.done(0)  # Mark first pending item as done

# Clear completed
todos.clear_done()
```

### Custom Data Provider

```python
import random
from termdash.widgets import SparklineWidget

def get_cpu_usage():
    return random.gauss(50, 10)  # Simulated CPU usage

widget = SparklineWidget(
    data_provider=get_cpu_usage,
    label="CPU %",
    max_points=50
)
```

### Log Widget

```python
from termdash.widgets import LogWidget

# Tail a log file
logs = LogWidget(log_file="/var/log/system.log", follow=True)

# Or add lines programmatically
logs.add_line("Application started", level="INFO")
logs.add_line("Connection established", level="SUCCESS")
```

## 🎨 Customization

### Widget Configuration

```python
from termdash.widget import WidgetConfig

config = WidgetConfig(
    name="mywidget",
    title="My Widget",
    refresh_interval=30.0,  # Update every 30 seconds
    border_style="bright_green",
    show_header=True,
    show_footer=True,
    padding=1
)

widget = SomeWidget(config=config)
```

### Custom Colors

Available border styles:
- Standard colors: `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`
- Bright variants: `bright_red`, `bright_green`, `bright_blue`, etc.
- Other: `black`, `grey`, `dim`

## 📁 Project Structure

```
termdash/
├── __init__.py          # Package exports
├── __main__.py          # CLI entry point
├── dashboard.py         # Main dashboard class
├── widget.py            # Base widget class
├── layout.py            # Layout managers
├── config.py            # Configuration management
├── widgets/             # Built-in widgets
│   ├── system.py        # System stats widgets
│   ├── weather.py       # Weather widget
│   ├── stocks.py        # Stock/crypto widgets
│   ├── todos.py         # Todo list widget
│   ├── clock.py         # Clock widgets
│   ├── text.py          # Text/log widgets
│   └── charts.py        # Chart widgets
├── examples/            # Example dashboards
│   ├── demo.py
│   ├── system_monitor.py
│   └── finance_dashboard.py
├── requirements.txt
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Areas to improve:

- More widget types (GitHub stats, calendar, RSS feeds, etc.)
- Additional layout options
- Theme support
- Better error handling
- Performance optimizations

## 📄 License

MIT License - feel free to use in your projects!

## 🙏 Credits

Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal UIs.
