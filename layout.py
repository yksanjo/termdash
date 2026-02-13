"""Layout management for TermDash dashboards."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass


@dataclass
class Position:
    """Position of a widget in the grid."""
    row: int
    col: int
    row_span: int = 1
    col_span: int = 1


class Layout(ABC):
    """Base layout class."""
    
    def __init__(self):
        self.widgets: Dict[str, 'Widget'] = {}
        self.positions: Dict[str, Position] = {}
    
    def add_widget(self, widget: 'Widget', position: Position) -> None:
        """Add a widget to the layout."""
        self.widgets[widget.config.name] = widget
        self.positions[widget.config.name] = position
    
    def remove_widget(self, name: str) -> Optional['Widget']:
        """Remove a widget from the layout."""
        if name in self.widgets:
            self.positions.pop(name, None)
            return self.widgets.pop(name)
        return None
    
    def get_widget(self, name: str) -> Optional['Widget']:
        """Get a widget by name."""
        return self.widgets.get(name)
    
    def get_position(self, name: str) -> Optional[Position]:
        """Get a widget's position."""
        return self.positions.get(name)
    
    @abstractmethod
    def arrange(self, available_width: int, available_height: int) -> Dict[str, Tuple[int, int, int, int]]:
        """
        Arrange widgets and return their positions as (x, y, width, height).
        Must be implemented by subclasses.
        """
        pass


class GridLayout(Layout):
    """Grid-based layout system."""
    
    def __init__(self, rows: int = 2, cols: int = 2, 
                 gap_x: int = 1, gap_y: int = 1):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.gap_x = gap_x
        self.gap_y = gap_y
    
    def add_widget(self, widget: 'Widget', row: int = 0, col: int = 0,
                   row_span: int = 1, col_span: int = 1) -> None:
        """Add a widget to a specific grid position."""
        position = Position(row, col, row_span, col_span)
        super().add_widget(widget, position)
    
    def arrange(self, available_width: int, available_height: int) -> Dict[str, Tuple[int, int, int, int]]:
        """
        Calculate widget positions in the grid.
        Returns dict of widget_name -> (x, y, width, height).
        """
        # Calculate cell dimensions
        total_gap_x = self.gap_x * (self.cols - 1)
        total_gap_y = self.gap_y * (self.rows - 1)
        
        cell_width = (available_width - total_gap_x) // self.cols
        cell_height = (available_height - total_gap_y) // self.rows
        
        positions = {}
        
        for name, widget in self.widgets.items():
            pos = self.positions[name]
            
            # Calculate position and size
            x = pos.col * (cell_width + self.gap_x)
            y = pos.row * (cell_height + self.gap_y)
            width = pos.col_span * cell_width + (pos.col_span - 1) * self.gap_x
            height = pos.row_span * cell_height + (pos.row_span - 1) * self.gap_y
            
            positions[name] = (x, y, width, height)
        
        return positions
    
    def get_available_cells(self) -> List[Tuple[int, int]]:
        """Get list of available (row, col) cells."""
        occupied = set()
        for pos in self.positions.values():
            for r in range(pos.row, pos.row + pos.row_span):
                for c in range(pos.col, pos.col + pos.col_span):
                    occupied.add((r, c))
        
        available = []
        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) not in occupied:
                    available.append((row, col))
        
        return available


class FlexLayout(Layout):
    """Flexbox-like layout that adapts to content."""
    
    def __init__(self, direction: str = "row", gap: int = 1):
        super().__init__()
        self.direction = direction  # "row" or "column"
        self.gap = gap
        self.widget_order: List[str] = []
    
    def add_widget(self, widget: 'Widget', flex: float = 1.0) -> None:
        """Add a widget with a flex value."""
        super().add_widget(widget, Position(0, 0))
        self.positions[widget.config.name] = {"flex": flex}
        if widget.config.name not in self.widget_order:
            self.widget_order.append(widget.config.name)
    
    def arrange(self, available_width: int, available_height: int) -> Dict[str, Tuple[int, int, int, int]]:
        """Arrange widgets using flex values."""
        if not self.widgets:
            return {}
        
        total_flex = sum(self.positions[name].get("flex", 1) for name in self.widget_order)
        total_gap = self.gap * (len(self.widget_order) - 1)
        
        positions = {}
        current_pos = 0
        
        for name in self.widget_order:
            flex = self.positions[name].get("flex", 1)
            ratio = flex / total_flex
            
            if self.direction == "row":
                width = int((available_width - total_gap) * ratio)
                height = available_height
                positions[name] = (current_pos, 0, width, height)
                current_pos += width + self.gap
            else:  # column
                width = available_width
                height = int((available_height - total_gap) * ratio)
                positions[name] = (0, current_pos, width, height)
                current_pos += height + self.gap
        
        return positions


class SplitLayout(Layout):
    """Split layout - divides space between two widgets."""
    
    def __init__(self, split_ratio: float = 0.5, vertical: bool = False):
        super().__init__()
        self.split_ratio = split_ratio
        self.vertical = vertical
        self.primary: Optional[str] = None
        self.secondary: Optional[str] = None
    
    def set_primary(self, widget: 'Widget') -> None:
        """Set the primary (left/top) widget."""
        self.add_widget(widget, Position(0, 0))
        self.primary = widget.config.name
    
    def set_secondary(self, widget: 'Widget') -> None:
        """Set the secondary (right/bottom) widget."""
        self.add_widget(widget, Position(0, 1))
        self.secondary = widget.config.name
    
    def arrange(self, available_width: int, available_height: int) -> Dict[str, Tuple[int, int, int, int]]:
        """Arrange the two widgets according to split ratio."""
        positions = {}
        
        if self.vertical:
            # Split vertically (top/bottom)
            primary_height = int(available_height * self.split_ratio)
            secondary_height = available_height - primary_height - 1
            
            if self.primary:
                positions[self.primary] = (0, 0, available_width, primary_height)
            if self.secondary:
                positions[self.secondary] = (0, primary_height + 1, available_width, secondary_height)
        else:
            # Split horizontally (left/right)
            primary_width = int(available_width * self.split_ratio)
            secondary_width = available_width - primary_width - 1
            
            if self.primary:
                positions[self.primary] = (0, 0, primary_width, available_height)
            if self.secondary:
                positions[self.secondary] = (primary_width + 1, 0, secondary_width, available_height)
        
        return positions
