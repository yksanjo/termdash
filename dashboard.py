"""Main dashboard class for TermDash."""

import asyncio
import signal
from typing import Optional, Dict, List, Callable
from datetime import datetime

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout as RichLayout
from rich.table import Table
from rich.align import Align

from .layout import Layout, GridLayout
from .widget import Widget, WidgetConfig


class Dashboard:
    """Main dashboard class that manages widgets and rendering."""
    
    def __init__(self, title: str = "TermDash", refresh_rate: float = 1.0):
        self.title = title
        self.refresh_rate = refresh_rate
        self.console = Console()
        self.layout: Layout = GridLayout(rows=2, cols=2)
        self.widgets: Dict[str, Widget] = {}
        self._running = False
        self._tasks: List[asyncio.Task] = []
        self._key_handlers: Dict[str, Callable] = {}
        self._global_handlers: List[Callable] = []
        self._status_message: str = ""
        self._status_time: Optional[datetime] = None
        
        # Setup default key handlers
        self._setup_default_keys()
    
    def _setup_default_keys(self) -> None:
        """Setup default keyboard shortcuts."""
        self._key_handlers['q'] = self.stop
        self._key_handlers['r'] = self.refresh_all
        self._key_handlers['h'] = self._show_help
    
    def add_widget(self, widget: Widget, **layout_kwargs) -> 'Dashboard':
        """Add a widget to the dashboard."""
        self.widgets[widget.config.name] = widget
        
        if isinstance(self.layout, GridLayout):
            # For grid layout, accept row/col positioning
            row = layout_kwargs.get('row', 0)
            col = layout_kwargs.get('col', 0)
            row_span = layout_kwargs.get('row_span', 1)
            col_span = layout_kwargs.get('col_span', 1)
            self.layout.add_widget(widget, row, col, row_span, col_span)
        else:
            self.layout.add_widget(widget, Position(0, 0))
        
        return self
    
    def remove_widget(self, name: str) -> Optional[Widget]:
        """Remove a widget from the dashboard."""
        self.layout.remove_widget(name)
        return self.widgets.pop(name, None)
    
    def set_layout(self, layout: Layout) -> 'Dashboard':
        """Set a custom layout."""
        self.layout = layout
        # Re-add all widgets to new layout
        for name, widget in self.widgets.items():
            pos = self.layout.get_position(name)
            if pos:
                self.layout.add_widget(widget, pos)
        return self
    
    def set_grid(self, rows: int = 2, cols: int = 2) -> 'Dashboard':
        """Set a grid layout."""
        self.layout = GridLayout(rows=rows, cols=cols)
        return self
    
    def bind_key(self, key: str, handler: Callable) -> 'Dashboard':
        """Bind a key to a handler function."""
        self._key_handlers[key] = handler
        return self
    
    def on_update(self, handler: Callable) -> 'Dashboard':
        """Add a global update handler."""
        self._global_handlers.append(handler)
        return self
    
    def set_status(self, message: str, duration: float = 3.0) -> None:
        """Set a status message."""
        self._status_message = message
        self._status_time = datetime.now()
        
        # Clear status after duration
        asyncio.create_task(self._clear_status(duration))
    
    async def _clear_status(self, delay: float) -> None:
        """Clear status message after delay."""
        await asyncio.sleep(delay)
        self._status_message = ""
        self._status_time = None
    
    async def refresh_all(self) -> None:
        """Refresh all widgets."""
        self.set_status("Refreshing all widgets...")
        tasks = [widget.update() for widget in self.widgets.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def _show_help(self) -> None:
        """Show help message."""
        help_text = """
        Keyboard Shortcuts:
        
        [b]q[/b] - Quit dashboard
        [b]r[/b] - Refresh all widgets
        [b]h[/b] - Show this help
        """
        self.console.print(Panel(help_text, title="Help", border_style="green"))
        input("\nPress Enter to continue...")
    
    def _render_header(self) -> Table:
        """Render the dashboard header."""
        header = Table.grid(expand=True)
        header.add_column(justify="left")
        header.add_column(justify="center")
        header.add_column(justify="right")
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = self._status_message if self._status_message else ""
        
        header.add_row(
            Text(f"⬡ {self.title}", style="bold cyan"),
            Text(status, style="yellow"),
            Text(now, style="dim")
        )
        
        return header
    
    def _render_footer(self) -> Table:
        """Render the dashboard footer."""
        footer = Table.grid(expand=True)
        footer.add_column(justify="left")
        footer.add_column(justify="center")
        footer.add_column(justify="right")
        
        widget_count = len(self.widgets)
        
        footer.add_row(
            Text(f"Widgets: {widget_count}", style="dim"),
            Text("Press 'h' for help, 'q' to quit", style="dim"),
            Text("● Live", style="green")
        )
        
        return footer
    
    def render(self) -> Panel:
        """Render the full dashboard."""
        # Get terminal size
        width = self.console.width - 4
        height = self.console.height - 8
        
        # Arrange widgets
        positions = self.layout.arrange(width, height)
        
        # Create rich layout
        rich_layout = RichLayout()
        rich_layout.split_column(
            RichLayout(name="header", size=3),
            RichLayout(name="main"),
            RichLayout(name="footer", size=1)
        )
        
        # Set header and footer
        rich_layout["header"].update(self._render_header())
        rich_layout["footer"].update(self._render_footer())
        
        # Render widgets into main area
        if positions:
            # For grid layout, create rows
            rows = {}
            for name, (x, y, w, h) in positions.items():
                row_key = y
                if row_key not in rows:
                    rows[row_key] = []
                rows[row_key].append((name, x, w, h))
            
            # Sort by row and then by x position
            sorted_rows = []
            for row_y in sorted(rows.keys()):
                row_widgets = sorted(rows[row_y], key=lambda x: x[1])
                sorted_rows.append(row_widgets)
            
            if sorted_rows:
                # Create row layouts
                row_layouts = [RichLayout(name=f"row_{i}") for i in range(len(sorted_rows))]
                rich_layout["main"].split_row(*row_layouts)
                
                for i, row_widgets in enumerate(sorted_rows):
                    if len(row_widgets) == 1:
                        # Single widget in row
                        name = row_widgets[0][0]
                        widget = self.widgets.get(name)
                        if widget:
                            rich_layout[f"row_{i}"].update(widget.render())
                    else:
                        # Multiple widgets - split column
                        col_layouts = [RichLayout(name=f"row_{i}_col_{j}") 
                                      for j in range(len(row_widgets))]
                        rich_layout[f"row_{i}"].split_column(*col_layouts)
                        
                        for j, (name, _, _, _) in enumerate(row_widgets):
                            widget = self.widgets.get(name)
                            if widget:
                                rich_layout[f"row_{i}_col_{j}"].update(widget.render())
        
        return Panel(rich_layout, border_style="blue")
    
    async def _update_loop(self) -> None:
        """Main update loop for the dashboard."""
        while self._running:
            # Update all widgets
            for widget in self.widgets.values():
                await widget.update()
            
            # Call global handlers
            for handler in self._global_handlers:
                try:
                    handler()
                except Exception:
                    pass
            
            await asyncio.sleep(self.refresh_rate)
    
    async def _keyboard_loop(self) -> None:
        """Handle keyboard input."""
        import sys
        import termios
        import tty
        
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            # Set terminal to raw mode
            tty.setcbreak(sys.stdin.fileno())
            
            while self._running:
                # Check for input (non-blocking)
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    if char in self._key_handlers:
                        handler = self._key_handlers[char]
                        if asyncio.iscoroutinefunction(handler):
                            await handler()
                        else:
                            handler()
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    def stop(self) -> None:
        """Stop the dashboard."""
        self._running = False
        for widget in self.widgets.values():
            widget.stop_auto_update()
    
    async def run_async(self) -> None:
        """Run the dashboard asynchronously."""
        self._running = True
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initial refresh
        await self.refresh_all()
        
        # Start widget auto-updates
        for widget in self.widgets.values():
            task = asyncio.create_task(widget.start_auto_update())
            self._tasks.append(task)
        
        # Start update loop
        update_task = asyncio.create_task(self._update_loop())
        self._tasks.append(update_task)
        
        # Start keyboard handler
        keyboard_task = asyncio.create_task(self._keyboard_loop())
        self._tasks.append(keyboard_task)
        
        # Main render loop
        with Live(self.render(), screen=True, refresh_per_second=4) as live:
            while self._running:
                live.update(self.render())
                await asyncio.sleep(0.25)
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        self._tasks.clear()
    
    def run(self) -> None:
        """Run the dashboard (blocking)."""
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            self.stop()
            self.console.print("\n[yellow]Dashboard stopped.[/yellow]")
