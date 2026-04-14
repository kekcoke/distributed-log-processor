"""JSON file writer for log output."""
import json
from typing import List
from .base import BaseWriter
from parsers.base import ParsedEntry


class JSONWriter(BaseWriter):
    """Write entries to a JSON file with array format."""
    
    def __init__(self, output_path: str, indent: int = 2):
        super().__init__(output_path)
        self.indent = indent
        self._initialized = False
    
    def write(self, entries: List[ParsedEntry]):
        """Write entries to JSON file."""
        # Read existing data
        existing = []
        if self.output_path.exists():
            try:
                content = self.output_path.read_text()
                if content.strip():
                    existing = json.loads(content)
                    if not isinstance(existing, list):
                        existing = [existing]
            except json.JSONDecodeError:
                existing = []
        
        # Append new entries
        for entry in entries:
            entry_dict = entry.to_dict()
            # Convert tags set to list for JSON
            if 'tags' in entry.metadata and isinstance(entry.metadata['tags'], set):
                entry_dict['tags'] = list(entry.metadata['tags'])
            existing.append(entry_dict)
        
        # Write back
        self.output_path.write_text(json.dumps(existing, indent=self.indent))
