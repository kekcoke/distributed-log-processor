"""Base parser class for all log formats."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class ParsedEntry:
    """Standardized log entry after parsing."""
    timestamp: Optional[datetime] = None
    level: Optional[str] = None
    message: str = ""
    source: str = "unknown"
    raw: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    format_type: str = "unknown"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'level': self.level,
            'message': self.message,
            'source': self.source,
            'raw': self.raw,
            'metadata': self.metadata,
            'format_type': self.format_type,
        }


class BaseParser(ABC):
    """Abstract base class for log parsers."""
    
    format_name: str = "base"
    
    @abstractmethod
    def parse(self, line: str) -> Optional[ParsedEntry]:
        """Parse a single log line into a ParsedEntry."""
        pass
    
    def parse_batch(self, lines: list) -> list:
        """Parse multiple lines."""
        entries = []
        for line in lines:
            entry = self.parse(line)
            if entry:
                entries.append(entry)
        return entries
