"""Windows Event Log parser."""
import re
from datetime import datetime
from .base import BaseParser, ParsedEntry


class WindowsEventParser(BaseParser):
    """Parser for Windows Event Log XML format."""
    
    format_name = "windows_event"
    
    LEVEL_MAP = {
        '0': 'INFO',      # LogAlways
        '1': 'CRITICAL',  # Critical
        '2': 'ERROR',     # Error
        '3': 'WARNING',   # Warning
        '4': 'INFO',      # Information
        '5': 'DEBUG',     # Verbose
    }
    
    def parse(self, line: str) -> ParsedEntry:
        """Parse Windows Event XML entry."""
        line = line.strip()
        if not line or not line.startswith('<Event'):
            return None
        
        entry = ParsedEntry(raw=line, format_type=self.format_name)
        
        # Extract EventID
        event_id_match = re.search(r'<EventID[^>]*>(\d+)</EventID>', line)
        if event_id_match:
            entry.metadata['event_id'] = int(event_id_match.group(1))
        
        # Extract Level
        level_match = re.search(r'<Level>(\d+)</Level>', line)
        if level_match:
            entry.level = self.LEVEL_MAP.get(level_match.group(1), 'INFO')
            entry.metadata['level_code'] = int(level_match.group(1))
        
        # Extract TimeCreated
        time_match = re.search(r'TimeCreated[^>]*SystemTime="([^"]+)"', line)
        if time_match:
            try:
                entry.timestamp = datetime.fromisoformat(time_match.group(1).replace('Z', '+00:00'))
            except:
                pass
        
        # Extract Provider Name
        provider_match = re.search(r'Name="([^"]+)"', line)
        if provider_match:
            entry.metadata['provider'] = provider_match.group(1)
            entry.source = provider_match.group(1)
        
        # Extract Message
        msg_match = re.search(r'<Message>([^<]+)</Message>', line)
        if msg_match:
            entry.message = msg_match.group(1)
        
        # Extract Computer
        computer_match = re.search(r'<Computer>([^<]+)</Computer>', line)
        if computer_match:
            entry.metadata['computer'] = computer_match.group(1)
        
        if not entry.message:
            entry.message = f"Windows Event {entry.metadata.get('event_id', 'Unknown')}"
        
        return entry
