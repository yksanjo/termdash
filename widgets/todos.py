"""Todo list widget for TermDash."""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Group

from ..widget import Widget, WidgetConfig


class TodoItem:
    """Single todo item."""
    
    def __init__(self, text: str, done: bool = False, 
                 priority: str = "medium", created: Optional[datetime] = None,
                 tags: Optional[List[str]] = None):
        self.text = text
        self.done = done
        self.priority = priority
        self.created = created or datetime.now()
        self.tags = tags or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "done": self.done,
            "priority": self.priority,
            "created": self.created.isoformat(),
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TodoItem":
        return cls(
            text=data["text"],
            done=data.get("done", False),
            priority=data.get("priority", "medium"),
            created=datetime.fromisoformat(data["created"]) if "created" in data else None,
            tags=data.get("tags", [])
        )


class TodoWidget(Widget):
    """Widget displaying and managing todo items."""
    
    PRIORITY_COLORS = {
        "high": "red",
        "medium": "yellow",
        "low": "green"
    }
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 storage_path: Optional[str] = None,
                 max_items: int = 10):
        if config is None:
            config = WidgetConfig(
                name="todos",
                title="✅ Todos",
                refresh_interval=5.0,
                border_style="green"
            )
        super().__init__(config)
        self.max_items = max_items
        self.items: List[TodoItem] = []
        self.storage_path = storage_path or os.path.expanduser("~/.termdash_todos.json")
        self._load()
    
    def _load(self) -> None:
        """Load todos from storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.items = [TodoItem.from_dict(item) for item in data]
        except Exception:
            self.items = []
    
    def _save(self) -> None:
        """Save todos to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump([item.to_dict() for item in self.items], f, indent=2)
        except Exception:
            pass
    
    async def fetch_data(self) -> Dict[str, Any]:
        """Return current todo state."""
        # Reload from disk to sync with other instances
        self._load()
        
        total = len(self.items)
        done = sum(1 for item in self.items if item.done)
        pending = total - done
        
        # Get high priority pending items
        high_priority = [
            item for item in self.items 
            if item.priority == "high" and not item.done
        ]
        
        return {
            "items": self.items,
            "total": total,
            "done": done,
            "pending": pending,
            "high_priority": high_priority
        }
    
    def render(self) -> Panel:
        """Render todo list."""
        if not self.data:
            return Panel("Loading...", title=self.config.title,
                        border_style=self.config.border_style)
        
        d = self.data
        items = d["items"]
        
        if not items:
            content = Text("No todos yet!\nAdd items with add_todo()", style="dim italic")
        else:
            # Show pending items first, then done items
            pending = [item for item in items if not item.done]
            done = [item for item in items if item.done]
            
            # Sort by priority
            priority_order = {"high": 0, "medium": 1, "low": 2}
            pending.sort(key=lambda x: priority_order.get(x.priority, 1))
            
            display_items = pending[:self.max_items]
            if len(display_items) < self.max_items:
                display_items.extend(done[:self.max_items - len(display_items)])
            
            table = Table(expand=True, box=None, show_header=False)
            table.add_column(width=3)  # Checkbox
            table.add_column()  # Text
            table.add_column(width=6, justify="right")  # Priority
            
            for item in display_items[:self.max_items]:
                checkbox = "✓" if item.done else "○"
                check_style = "green" if item.done else "white"
                
                text = item.text
                if item.done:
                    text_style = "dim strike"
                else:
                    text_style = "white"
                
                priority_color = self.PRIORITY_COLORS.get(item.priority, "white")
                priority_text = Text(item.priority[:1].upper(), style=priority_color)
                
                table.add_row(
                    Text(checkbox, style=check_style),
                    Text(text, style=text_style),
                    priority_text
                )
            
            # Show count if truncated
            remaining = len(pending) + len(done) - len(display_items)
            if remaining > 0:
                table.add_row("", Text(f"... and {remaining} more", style="dim italic"), "")
            
            content = table
        
        # Stats footer
        stats = f"Done: {d['done']} | Pending: {d['pending']}"
        if d['high_priority']:
            stats += f" | ⚠️  High: {len(d['high_priority'])}"
        
        return Panel(
            content,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style,
            subtitle=stats if self.config.show_footer else None
        )
    
    def add(self, text: str, priority: str = "medium", tags: Optional[List[str]] = None) -> None:
        """Add a new todo item."""
        item = TodoItem(text, priority=priority, tags=tags)
        self.items.append(item)
        self._save()
    
    def done(self, index: int) -> bool:
        """Mark item at index as done."""
        pending = [item for item in self.items if not item.done]
        if 0 <= index < len(pending):
            pending[index].done = True
            self._save()
            return True
        return False
    
    def remove(self, index: int) -> bool:
        """Remove item at index."""
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self._save()
            return True
        return False
    
    def clear_done(self) -> int:
        """Remove all done items. Returns count removed."""
        original_count = len(self.items)
        self.items = [item for item in self.items if not item.done]
        removed = original_count - len(self.items)
        if removed > 0:
            self._save()
        return removed
    
    def clear_all(self) -> None:
        """Remove all items."""
        self.items = []
        self._save()
