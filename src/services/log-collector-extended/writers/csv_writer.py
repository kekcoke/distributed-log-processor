"""CSV file writer for log output."""
import csv
from typing import List
from .base import BaseWriter
from parsers.base import ParsedEntry


class CSVWriter(BaseWriter):
    """Write entries to a CSV file."""
    
    def __init__(self, output_path: str):
        super().__init__(output_path)
        self._fieldnames = ['timestamp', 'level', 'message', 'source', 'format_type', 'raw', 'tags', 'metadata']
    
    def write(self, entries: List[ParsedEntry]):
        """Write entries to CSV file."""
        write_header = not self.output_path.exists() or self.output_path.stat().st_size == 0
        
        with open(self.output_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self._fieldnames)
            
            if write_header:
                writer.writeheader()
            
            for entry in entries:
                entry_dict = entry.to_dict()
                # Flatten tags and metadata
                entry_dict['tags'] = ','.join(entry.metadata.get('tags', []))
                entry_dict['metadata'] = str(entry.metadata)
                writer.writerow(entry_dict)
