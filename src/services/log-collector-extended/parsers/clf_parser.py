"""Common Log Format (CLF) parser."""
import re
from datetime import datetime
from .base import BaseParser, ParsedEntry


class CLFParser(BaseParser):
    """Parser for Apache/Nginx Common Log Format.
    
    Format: host ident authuser [timestamp] "method url protocol" status size
    
    Example: 127.0.0.1 - - [10/Oct/2024:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 2326
    """
    
    format_name = "clf"
    
    MONTH_MAP = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    
    def parse(self, line: str) -> ParsedEntry:
        """Parse CLF entry."""
        line = line.strip()
        if not line or ' - - ' not in line:
            return None
        
        entry = ParsedEntry(raw=line, format_type=self.format_name)
        
        # Pattern: host - - [timestamp] "method url protocol" status size
        pattern = r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\S+)'
        match = re.match(pattern, line)
        
        if match:
            groups = match.groups()
            entry.source = groups[0]  # host IP
            entry.metadata['method'] = groups[2]
            entry.metadata['url'] = groups[3]
            entry.metadata['protocol'] = groups[4]
            
            status = int(groups[5])
            entry.metadata['status'] = status
            
            # Map HTTP status to level
            if status >= 500:
                entry.level = 'ERROR'
            elif status >= 400:
                entry.level = 'WARNING'
            elif status >= 300:
                entry.level = 'INFO'
            else:
                entry.level = 'DEBUG'
            
            entry.metadata['size'] = groups[6]
            
            # Parse timestamp
            try:
                ts_str = groups[1]
                day, month_str, year, time_str = ts_str.split('/')
                month = self.MONTH_MAP.get(month_str, 1)
                time_part = time_str.split()[0]
                entry.timestamp = datetime.strptime(f"{day} {month} {year} {time_part}", "%d %m %Y %H:%M:%S")
            except:
                pass
            
            entry.message = f"{groups[2]} {groups[3]} -> {status}"
        else:
            entry.message = line
        
        return entry
