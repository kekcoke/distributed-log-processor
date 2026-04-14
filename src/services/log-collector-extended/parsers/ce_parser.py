"""Cisco IOS Syslog (CE - Cisco Erase) parser."""
import re
from datetime import datetime
from .base import BaseParser, ParsedEntry


class CEParser(BaseParser):
    """Parser for Cisco IOS Syslog format.
    
    Format: timestamp hostname %FACILITY-SEVERITY-MNEMONIC: message
    
    Example: Jan 15 10:30:45.123 router %SYS-5-CONFIG_I: Configuration saved
    """
    
    format_name = "ce"
    
    SEVERITY_MAP = {
        '0': 'EMERGENCY', '1': 'ALERT', '2': 'CRITICAL', '3': 'ERROR',
        '4': 'WARNING', '5': 'NOTICE', '6': 'INFO', '7': 'DEBUG'
    }
    
    def parse(self, line: str) -> ParsedEntry:
        """Parse Cisco Syslog entry."""
        line = line.strip()
        if not line or '%' not in line:
            return None
        
        entry = ParsedEntry(raw=line, format_type=self.format_name)
        
        # Match: Jan 15 10:30:45 hostname %FACILITY-SEVERITY-MNEMONIC: message
        pattern = r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s+(\S+)\s+(?:%(\w+)-(\d)-(\w+):)\s*(.*)$'
        match = re.match(pattern, line)
        
        if match:
            groups = match.groups()
            # Parse timestamp - assume current year
            try:
                ts_str = f"{datetime.now().year} {groups[0]}"
                entry.timestamp = datetime.strptime(ts_str, '%Y %b %d %H:%M:%S.%f')[:6]
                entry.timestamp = datetime.strptime(ts_str.replace('.', ' ').split()[0], '%Y %b %d %H:%M:%S')
            except:
                pass
            
            entry.source = groups[1]  # hostname
            entry.metadata['facility'] = groups[2]
            entry.level = self.SEVERITY_MAP.get(groups[3], 'INFO')
            entry.metadata['mnemonic'] = groups[4]
            entry.message = groups[5]
        else:
            entry.message = line
        
        return entry
