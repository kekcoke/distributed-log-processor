"""Base writer class for log output."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from parsers.base import ParsedEntry


class BaseWriter(ABC):
    """Abstract base class for log writers."""
    
    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Create output directory if it doesn't exist."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def write(self, entries: List[ParsedEntry]):
        """Write entries to output."""
        pass
    
    def write_entry(self, entry: ParsedEntry):
        """Write a single entry."""
        self.write([entry])
