"""Text-based widgets for TermDash."""

import os
from datetime import datetime
from typing import Optional, List, Callable
from collections import deque

from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.console import Group
from rich.table import Table

from ..widget import Widget, WidgetConfig


class LogWidget(Widget):
    """Widget displaying log output."""
    
    LEVEL_COLORS = {
        "DEBUG": "dim",
        "INFO": "blue",
        "WARNING": "yellow",
        "WARN": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red",
        "SUCCESS": "green"
    }
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 max_lines: int = 20,
                 log_file: Optional[str] = None,
                 follow: bool = False):
        if config is None:
            config = WidgetConfig(
                name="log",
                title="📝 Logs",
                refresh_interval=2.0,
                border_style="dim"
            )
        super().__init__(config)
        self.max_lines = max_lines
        self.log_file = log_file
        self.follow = follow
        self.lines: deque[str] = deque(maxlen=max_lines)
        self._file_pos = 0
    
    async def fetch_data(self) -> List[str]:
        """Read log lines."""
        if self.log_file and os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    if self.follow:
                        f.seek(self._file_pos)
                        new_lines = f.readlines()
                        self._file_pos = f.tell()
                        for line in new_lines:
                            self.lines.append(line.rstrip())
                    else:
                        # Read last N lines
                        f.seek(0, 2)  # End of file
                        lines = []
                        while len(lines) < self.max_lines:
                            try:
                                f.seek(-1024, 1)
                            except:
                                f.seek(0)
                                break
                            chunk = f.read(1024)
                            lines = chunk.split('\n')
                        self.lines = deque(lines[-self.max_lines:], maxlen=self.max_lines)
            except Exception as e:
                self.lines.append(f"Error reading log: {e}")
        
        return list(self.lines)
    
    def render(self) -> Panel:
        """Render log lines."""
        lines = self.data if self.data else []
        
        if not lines:
            content = Text("No log entries", style="dim italic")
        else:
            # Format lines with colors
            text_lines = []
            for line in lines[-self.max_lines:]:
                # Try to detect log level
                color = "white"
                for level, lvl_color in self.LEVEL_COLORS.items():
                    if level in line.upper():
                        color = lvl_color
                        break
                
                # Truncate long lines
                display_line = line[:100] + "..." if len(line) > 100 else line
                text_lines.append(Text(display_line, style=color))
            
            content = Group(*text_lines)
        
        return Panel(
            content,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style,
            padding=(0, 1)
        )
    
    def add_line(self, line: str, level: str = "INFO") -> None:
        """Add a log line."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {line}"
        self.lines.append(formatted)
    
    def clear(self) -> None:
        """Clear all log lines."""
        self.lines.clear()


class QuoteWidget(Widget):
    """Widget displaying rotating quotes or messages."""
    
    QUOTES = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Stay hungry, stay foolish. - Steve Jobs",
        "Code is like humor. When you have to explain it, it's bad. - Cory House",
        "First, solve the problem. Then, write the code. - John Johnson",
        "Simplicity is the soul of efficiency. - Austin Freeman",
        "Make it work, make it right, make it fast. - Kent Beck",
    ]
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 quotes: Optional[List[str]] = None,
                 rotate_interval: int = 5):
        if config is None:
            config = WidgetConfig(
                name="quote",
                title="💬 Quote",
                refresh_interval=30.0,
                border_style="magenta"
            )
        super().__init__(config)
        self.quotes = quotes or self.QUOTES
        self.rotate_interval = rotate_interval
        self._current_index = 0
        self._refresh_count = 0
    
    async def fetch_data(self) -> dict:
        """Get current quote."""
        self._refresh_count += 1
        
        # Rotate quote every N refreshes
        if self._refresh_count >= self.rotate_interval:
            self._current_index = (self._current_index + 1) % len(self.quotes)
            self._refresh_count = 0
        
        return {
            "quote": self.quotes[self._current_index],
            "index": self._current_index,
            "total": len(self.quotes)
        }
    
    def render(self) -> Panel:
        """Render quote."""
        if not self.data:
            return Panel("Loading...", title=self.config.title,
                        border_style=self.config.border_style)
        
        quote_text = Text(self.data["quote"], style="italic", justify="center")
        
        content = Table.grid(expand=True)
        content.add_column(justify="center")
        content.add_row("")
        content.add_row(quote_text)
        content.add_row("")
        
        return Panel(
            content,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style
        )


class CodeWidget(Widget):
    """Widget for displaying code snippets."""
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 code: str = "",
                 language: str = "python",
                 file_path: Optional[str] = None):
        if config is None:
            config = WidgetConfig(
                name="code",
                title="📄 Code",
                refresh_interval=60.0,
                border_style="blue"
            )
        super().__init__(config)
        self.code = code
        self.language = language
        self.file_path = file_path
    
    async def fetch_data(self) -> str:
        """Load code from file if specified."""
        if self.file_path and os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    return f.read()
            except Exception as e:
                return f"# Error loading file: {e}"
        return self.code
    
    def render(self) -> Panel:
        """Render code with syntax highlighting."""
        code = self.data if self.data else self.code
        
        if not code:
            return Panel("No code to display", title=self.config.title,
                        border_style=self.config.border_style)
        
        # Limit code length
        lines = code.split('\n')[:20]
        display_code = '\n'.join(lines)
        if len(code.split('\n')) > 20:
            display_code += "\n\n# ... (truncated)"
        
        syntax = Syntax(
            display_code,
            self.language,
            theme="monokai",
            line_numbers=True,
            word_wrap=True
        )
        
        return Panel(
            syntax,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style,
            padding=(0, 0)
        )
