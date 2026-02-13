"""System monitoring widgets."""

import psutil
import platform
from datetime import datetime
from typing import List, Optional
from collections import deque

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Group

from ..widget import Widget, WidgetConfig


class SystemStatsWidget(Widget):
    """Widget displaying comprehensive system statistics."""
    
    def __init__(self, config: Optional[WidgetConfig] = None):
        if config is None:
            config = WidgetConfig(
                name="system",
                title="🖥️  System Stats",
                refresh_interval=2.0,
                border_style="cyan"
            )
        super().__init__(config)
        self.history_size = 60
        self.cpu_history: deque[float] = deque(maxlen=self.history_size)
        self.memory_history: deque[float] = deque(maxlen=self.history_size)
    
    async def fetch_data(self) -> dict:
        """Fetch system statistics."""
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory info
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk info
        disk = psutil.disk_usage('/')
        
        # Boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        # Update history
        self.cpu_history.append(cpu_percent)
        self.memory_history.append(memory.percent)
        
        return {
            "cpu_percent": cpu_percent,
            "cpu_count": cpu_count,
            "cpu_freq": cpu_freq.current if cpu_freq else 0,
            "memory": memory,
            "swap": swap,
            "disk": disk,
            "uptime": uptime,
            "platform": platform.system(),
        }
    
    def render(self) -> Panel:
        """Render system stats."""
        if not self.data:
            return Panel("Loading...", title=self.config.title, 
                        border_style=self.config.border_style)
        
        d = self.data
        
        # Create main content
        content = Table.grid(expand=True)
        content.add_column()
        content.add_column()
        
        # CPU info with progress bar
        cpu_color = "green" if d["cpu_percent"] < 50 else "yellow" if d["cpu_percent"] < 80 else "red"
        cpu_progress = Progress(
            BarColumn(bar_width=None),
            TextColumn(f" {d['cpu_percent']:.1f}%"),
            expand=True
        )
        cpu_progress.add_task("CPU", total=100, completed=d["cpu_percent"])
        
        content.add_row(
            Text("CPU", style="bold"),
            cpu_progress
        )
        content.add_row(
            Text(f"  {d['cpu_count']} cores @ {d['cpu_freq']:.0f} MHz", style="dim"),
            Text("")
        )
        
        # Memory info
        mem = d["memory"]
        mem_color = "green" if mem.percent < 70 else "yellow" if mem.percent < 90 else "red"
        mem_progress = Progress(
            BarColumn(bar_width=None),
            TextColumn(f" {mem.percent:.1f}%"),
            expand=True
        )
        mem_progress.add_task("Memory", total=100, completed=mem.percent)
        
        content.add_row(
            Text("Memory", style="bold"),
            mem_progress
        )
        content.add_row(
            Text(f"  {self._format_bytes(mem.used)} / {self._format_bytes(mem.total)}", style="dim"),
            Text("")
        )
        
        # Disk info
        disk = d["disk"]
        disk_percent = (disk.used / disk.total) * 100
        disk_progress = Progress(
            BarColumn(bar_width=None),
            TextColumn(f" {disk_percent:.1f}%"),
            expand=True
        )
        disk_progress.add_task("Disk", total=100, completed=disk_percent)
        
        content.add_row(
            Text("Disk", style="bold"),
            disk_progress
        )
        content.add_row(
            Text(f"  {self._format_bytes(disk.used)} / {self._format_bytes(disk.total)}", style="dim"),
            Text("")
        )
        
        # Uptime
        uptime = d["uptime"]
        uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds // 60) % 60}m"
        content.add_row(
            Text("Uptime", style="bold"),
            Text(uptime_str)
        )
        
        footer = self.get_footer_text() if self.config.show_footer else None
        
        return Panel(
            content,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style,
            padding=(self.config.padding, self.config.padding),
            subtitle=footer
        )
    
    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes to human readable."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"


class CPUMemoryWidget(Widget):
    """Compact CPU and Memory widget."""
    
    def __init__(self, config: Optional[WidgetConfig] = None):
        if config is None:
            config = WidgetConfig(
                name="cpumem",
                title="⚡ CPU & Memory",
                refresh_interval=1.0,
                border_style="yellow"
            )
        super().__init__(config)
        self.cpu_history: deque[float] = deque(maxlen=30)
        self.mem_history: deque[float] = deque(maxlen=30)
    
    async def fetch_data(self) -> dict:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        
        self.cpu_history.append(cpu)
        self.mem_history.append(mem.percent)
        
        return {
            "cpu": cpu,
            "memory": mem,
            "cpu_history": list(self.cpu_history),
            "mem_history": list(self.mem_history)
        }
    
    def render(self) -> Panel:
        if not self.data:
            return Panel("Loading...", title=self.config.title,
                        border_style=self.config.border_style)
        
        d = self.data
        
        # Create sparkline for CPU
        cpu_spark = self._sparkline(d["cpu_history"], 50)
        mem_spark = self._sparkline(d["mem_history"], 50)
        
        table = Table.grid(expand=True)
        table.add_column(style="bold")
        table.add_column()
        
        cpu_color = "green" if d["cpu"] < 50 else "yellow" if d["cpu"] < 80 else "red"
        mem_color = "green" if d["memory"].percent < 70 else "yellow" if d["memory"].percent < 90 else "red"
        
        table.add_row(
            Text("CPU", style=cpu_color),
            Text(f"{d['cpu']:.1f}% {cpu_spark}", style=cpu_color)
        )
        table.add_row(
            Text("MEM", style=mem_color),
            Text(f"{d['memory'].percent:.1f}% {mem_spark}", style=mem_color)
        )
        
        return Panel(
            table,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style
        )
    
    def _sparkline(self, data: List[float], max_val: float = 100) -> str:
        """Create ASCII sparkline."""
        if not data:
            return ""
        
        blocks = "▁▂▃▄▅▆▇█"
        result = ""
        for val in data[-20:]:  # Show last 20 points
            idx = int((val / max_val) * (len(blocks) - 1))
            idx = min(idx, len(blocks) - 1)
            result += blocks[idx]
        return result


class DiskWidget(Widget):
    """Disk usage widget."""
    
    def __init__(self, config: Optional[WidgetConfig] = None, 
                 paths: Optional[List[str]] = None):
        if config is None:
            config = WidgetConfig(
                name="disk",
                title="💾 Disk Usage",
                refresh_interval=30.0,
                border_style="magenta"
            )
        super().__init__(config)
        self.paths = paths or ['/']
    
    async def fetch_data(self) -> List[dict]:
        results = []
        for path in self.paths:
            try:
                usage = psutil.disk_usage(path)
                results.append({
                    "path": path,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": (usage.used / usage.total) * 100
                })
            except Exception as e:
                results.append({
                    "path": path,
                    "error": str(e)
                })
        return results
    
    def render(self) -> Panel:
        if not self.data:
            return Panel("Loading...", title=self.config.title,
                        border_style=self.config.border_style)
        
        table = Table(expand=True, box=None)
        table.add_column("Path", style="cyan")
        table.add_column("Usage", style="green")
        table.add_column("Free", style="dim")
        
        for disk in self.data:
            if "error" in disk:
                table.add_row(disk["path"], f"Error: {disk['error']}", "")
            else:
                bar = self._progress_bar(disk["percent"])
                table.add_row(
                    disk["path"],
                    f"{bar} {disk['percent']:.1f}%",
                    self._format_bytes(disk["free"])
                )
        
        return Panel(
            table,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style
        )
    
    def _progress_bar(self, percent: float, width: int = 15) -> str:
        """Create ASCII progress bar."""
        filled = int((percent / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        return bar
    
    def _format_bytes(self, bytes_val: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"


class NetworkWidget(Widget):
    """Network usage widget."""
    
    def __init__(self, config: Optional[WidgetConfig] = None):
        if config is None:
            config = WidgetConfig(
                name="network",
                title="🌐 Network",
                refresh_interval=2.0,
                border_style="blue"
            )
        super().__init__(config)
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.last_time = None
    
    async def fetch_data(self) -> dict:
        stats = psutil.net_io_counters()
        current_time = datetime.now()
        
        # Calculate speeds
        upload_speed = 0
        download_speed = 0
        
        if self.last_time is not None:
            time_delta = (current_time - self.last_time).total_seconds()
            if time_delta > 0:
                upload_speed = (stats.bytes_sent - self.last_bytes_sent) / time_delta
                download_speed = (stats.bytes_recv - self.last_bytes_recv) / time_delta
        
        self.last_bytes_sent = stats.bytes_sent
        self.last_bytes_recv = stats.bytes_recv
        self.last_time = current_time
        
        # Get network connections
        connections = len(psutil.net_connections())
        
        return {
            "upload_speed": upload_speed,
            "download_speed": download_speed,
            "bytes_sent": stats.bytes_sent,
            "bytes_recv": stats.bytes_recv,
            "connections": connections,
            "packets_sent": stats.packets_sent,
            "packets_recv": stats.packets_recv,
        }
    
    def render(self) -> Panel:
        if not self.data:
            return Panel("Loading...", title=self.config.title,
                        border_style=self.config.border_style)
        
        d = self.data
        
        table = Table.grid(expand=True)
        table.add_column(style="bold cyan")
        table.add_column(style="green")
        table.add_column(style="dim")
        
        table.add_row(
            "▲ Upload",
            self._format_speed(d["upload_speed"]),
            f"Total: {self._format_bytes(d['bytes_sent'])}"
        )
        table.add_row(
            "▼ Download",
            self._format_speed(d["download_speed"]),
            f"Total: {self._format_bytes(d['bytes_recv'])}"
        )
        table.add_row(
            "# Connections",
            str(d["connections"]),
            ""
        )
        
        return Panel(
            table,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style
        )
    
    def _format_speed(self, bytes_per_sec: float) -> str:
        """Format speed in human readable format."""
        return f"{self._format_bytes(int(bytes_per_sec))}/s"
    
    def _format_bytes(self, bytes_val: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} TB"
