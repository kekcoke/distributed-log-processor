"""Plain text log parser."""
import re
from datetime import datetime
from .base import BaseParser, ParsedEntry


class PlainTextParser(BaseParser):
    """Parser for plain text logs with optional structured fields."""
    
    format_name = "plaintext"
    
    # Common patterns: 2024-01-15 10:30:45 [INFO] Message
    PATTERNS = [
        # ISO timestamp with level
        re.compile(r'^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s*\[?(INFO|WARN|WARNING|ERROR|DEBUG|CRITICAL|FATAL)\]?\s*[:\-]?\s*(.*)$', re.IGNORECASE),
        # Syslog style: Jan 15 10:30:45 hostname app: message
        re.compile(r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+\S+\s+\S+:\s*(.*)$'),
        # Simple timestamp: 10:30:45 [LEVEL] message
        re.compile(r'^(\d{2}:\d{2}:\d{2})\s*\[?(INFO|WARN|WARNING|ERROR|DEBUG|CRITICAL|FATAL)\]?\s*[:\-]?\s*(.*)$', re.IGNORECASE),
    ]
    
    LEVEL_MAP = {
        'warn': 'WARNING',
        'warning': 'WARNING',
        'error': 'ERROR',
        'debug': 'DEBUG',
        'critical': 'CRITICAL',
        'fatal': 'CRITICAL',
        'info': 'INFO',
    }
    
    def parse(self, line: str) -> ParsedEntry:
        """Parse a plain text log line."""
        line = line.strip()
        if not line:
            return None
        
        for pattern in self.PATTERNS:
            match = pattern.match(line)
            if match:
                groups = match.groups()
                entry = ParsedEntry(raw=line, format_type=self.format_name)
                
                # Try to parse timestamp
                try:
                    ts_str = groups[0]
                    for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%b %d %H:%M:%S', '%H:%M:%S']:
                        try:
                            entry.timestamp = datetime.strptime(ts_str, fmt)
                            break
                        except ValueError:
                            continue
                except:
                    pass
                
                # Extract level
                if len(groups) >= 2:
                    level_raw = groups[1].upper() if isinstance(groups[1], str) else None
                    if level_raw:
                        entry.level = self.LEVEL_MAP.get(level_raw.lower(), level_raw)
                
                # Extract message
                entry.message = groups[-1].strip()
                
                return entry
        
        # No pattern matched - return as raw message
        return ParsedEntry(
            message=line,
            raw=line,
            format_type=self.format_name
        )
