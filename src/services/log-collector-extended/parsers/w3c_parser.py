"""W3C Extended Log Format parser."""
import re
from datetime import datetime
from .base import BaseParser, ParsedEntry


class W3CParser(BaseParser):
    """Parser for W3C Extended Log Format.
    
    Format: Lines starting with #Fields define column order
    
    Example:
    #Fields: date time c-ip s-ip s-port cs-method cs-uri sc-status
    2024-01-15 10:30:45 192.168.1.1 10.0.0.1 80 GET /index.html 200
    """
    
    format_name = "w3c"
    
    def __init__(self):
        super().__init__()
        self.fields = []
        self.field_map = {}
    
    def parse_header(self, line: str):
        """Parse #Fields directive."""
        match = re.match(r'#Fields:\s*(.*)', line)
        if match:
            self.fields = match.group(1).split()
            self.field_map = {name: idx for idx, name in enumerate(self.fields)}
    
    def parse(self, line: str) -> ParsedEntry:
        """Parse W3C entry."""
        line = line.strip()
        if not line:
            return None
        
        entry = ParsedEntry(raw=line, format_type=self.format_name)
        
        # Parse header if present
        if line.startswith('#Fields:'):
            self.parse_header(line)
            return None  # Headers don't produce entries
        
        # Skip other directives
        if line.startswith('#'):
            return None
        
        # Split by whitespace
        parts = line.split()
        
        if not parts:
            return None
        
        # Extract date and time
        if 'date' in self.field_map:
            entry.metadata['date'] = parts[self.field_map['date']]
        if 'time' in self.field_map:
            entry.metadata['time'] = parts[self.field_map['time']]
        
        # Parse timestamp
        date_val = parts[self.field_map['date']] if 'date' in self.field_map else None
        time_val = parts[self.field_map['time']] if 'time' in self.field_map else None
        if date_val and time_val:
            try:
                entry.timestamp = datetime.strptime(f"{date_val} {time_val}", "%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        # Extract client IP
        if 'c-ip' in self.field_map:
            entry.source = parts[self.field_map['c-ip']]
        
        # Extract HTTP method and URL
        if 'cs-method' in self.field_map:
            entry.metadata['method'] = parts[self.field_map['cs-method']]
        if 'cs-uri' in self.field_map:
            entry.metadata['uri'] = parts[self.field_map['cs-uri']]
        
        # Extract status code
        if 'sc-status' in self.field_map:
            try:
                status = int(parts[self.field_map['sc-status']])
                entry.metadata['status'] = status
                if status >= 500:
                    entry.level = 'ERROR'
                elif status >= 400:
                    entry.level = 'WARNING'
                else:
                    entry.level = 'INFO'
            except:
                pass
        
        entry.message = entry.metadata.get('method', 'REQUEST') + ' ' + entry.metadata.get('uri', '')
        return entry
