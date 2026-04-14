"""Composite filter combining multiple filters."""
from typing import List
from .base import BaseFilter
from parsers.base import ParsedEntry


class CompositeFilter(BaseFilter):
    """Combine multiple filters with AND/OR logic."""
    
    def __init__(self, filters: List[BaseFilter] = None, mode: str = 'AND'):
        """
        Args:
            filters: List of filter instances
            mode: 'AND' (all must pass) or 'OR' (any must pass)
        """
        self.filters = filters or []
        self.mode = mode.upper()
    
    def add_filter(self, filter_instance: BaseFilter):
        """Add a filter to the composite."""
        self.filters.append(filter_instance)
    
    def should_include(self, entry: ParsedEntry) -> bool:
        if not self.filters:
            return True
        
        if self.mode == 'OR':
            return any(f.should_include(entry) for f in self.filters)
        else:  # AND mode (default)
            return all(f.should_include(entry) for f in self.filters)
