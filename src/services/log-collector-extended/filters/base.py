"""Base filter class for log filtering."""
from abc import ABC, abstractmethod
from typing import List
from parsers.base import ParsedEntry


class BaseFilter(ABC):
    """Abstract base class for log filters."""
    
    @abstractmethod
    def should_include(self, entry: ParsedEntry) -> bool:
        """Return True if entry should be included, False if filtered out."""
        pass
    
    def filter(self, entries: List[ParsedEntry]) -> List[ParsedEntry]:
        """Filter a list of entries."""
        return [e for e in entries if self.should_include(e)]
