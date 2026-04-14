"""Extended Log Format (ELF) parser."""
import re
from datetime import datetime
from .base import BaseParser, ParsedEntry


class ELFParser(BaseParser):
    """Parser for Extended Log Format (ELF/W3C).
    
    Format: Tab or space-separated fields with optional headers
    
    Example with W3C fields: date time c-ip s-ip s-port cs-method cs-uri cs-uri-stem sc-status
    """
    
    format_name = "elf"
    
    def parse(self, line: str) -> ParsedEntry:
        """Parse ELF entry."""
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        
        entry = ParsedEntry(raw=line, format_type=self.format_name)
        
        # Split by tabs or multiple spaces
        parts = re.split(r'\t+|\s{2,}', line)
        
        if len(parts) >= 4:
            entry.metadata['fields'] = parts
            
            # Try to identify common fields
            field_count = len(parts)
            
            # Common patterns: date, time, client_ip, server_ip, port, method, uri, status
            if field_count >= 1:
                entry.metadata['date'] = parts[0]
            if field_count >= 2:
                entry.metadata['time'] = parts[1]
            if field_count >= 3:
                entry.source = parts[2]  # Usually client IP
            
            # HTTP method indicator
            for part in parts:
                if part.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    entry.metadata['method'] = part.upper()
                    entry.message = f"{part.upper()} request"
                    break
            
            # Status code (numeric)
            for part in parts[-3:]:
                if part.isdigit() and 100 <= int(part) < 600:
                    status = int(part)
                    entry.metadata['status'] = status
                    if status >= 500:
                        entry.level = 'ERROR'
                    elif status >= 400:
                        entry.level = 'WARNING'
                    else:
                        entry.level = 'INFO'
                    break
            
            if not entry.message:
                entry.message = ' '.join(parts[:3])
        
        return entry
