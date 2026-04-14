"""NDJSON (Newline Delimited JSON) writer for log output."""
import json
from typing import List
from .base import BaseWriter
from parsers.base import ParsedEntry


class NDJSONWriter(BaseWriter):
    """Write entries to NDJSON file (one JSON object per line)."""
    
    def write(self, entries: List[ParsedEntry]):
        """Write entries as NDJSON (append mode)."""
        with open(self.output_path, 'a') as f:
            for entry in entries:
                entry_dict = entry.to_dict()
                # Convert tags set to list for JSON
                if 'tags' in entry.metadata and isinstance(entry.metadata['tags'], set):
                    entry_dict['tags'] = list(entry.metadata['tags'])
                f.write(json.dumps(entry_dict) + '\n')
