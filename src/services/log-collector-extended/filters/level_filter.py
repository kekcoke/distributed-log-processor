"""Level-based filter for log filtering."""
from typing import List, Set
from .base import BaseFilter
from parsers.base import ParsedEntry


class LevelFilter(BaseFilter):
    """Filter entries based on log level."""
    
    LEVEL_PRIORITY = {
        'DEBUG': 10,
        'INFO': 20,
        'NOTICE': 25,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50,
        'ALERT': 60,
        'EMERGENCY': 70,
    }
    
    def __init__(self, include_levels: List[str] = None, 
                 exclude_levels: List[str] = None,
                 min_level: str = None):
        """
        Args:
            include_levels: Only include these levels (e.g., ['ERROR', 'CRITICAL'])
            exclude_levels: Exclude these levels (e.g., ['DEBUG', 'INFO'])
            min_level: Include this level and above (e.g., 'WARNING' includes WARNING, ERROR, CRITICAL)
        """
        self.include_levels = {l.upper() for l in (include_levels or [])} if include_levels else set()
        self.exclude_levels = {l.upper() for l in (exclude_levels or [])} if exclude_levels else set()
        self.min_level = self.LEVEL_PRIORITY.get(min_level.upper() if min_level else '', 0)
    
    def should_include(self, entry: ParsedEntry) -> bool:
        level = (entry.level or 'INFO').upper()
        
        # Exclude check takes priority
        if self.exclude_levels and level in self.exclude_levels:
            return False
        
        # Include levels filter
        if self.include_levels:
            return level in self.include_levels
        
        # Minimum level filter
        entry_priority = self.LEVEL_PRIORITY.get(level, 0)
        return entry_priority >= self.min_level
