"""Regex-based filter for log filtering."""
import re
from typing import List, Optional
from .base import BaseFilter
from parsers.base import ParsedEntry


class RegexFilter(BaseFilter):
    """Filter entries based on regex patterns."""
    
    def __init__(self, include_patterns: List[str] = None, 
                 exclude_patterns: List[str] = None,
                 field: str = 'message'):
        """
        Args:
            include_patterns: List of regex patterns - entry must match at least one to be included
            exclude_patterns: List of regex patterns - entry is excluded if it matches any
            field: Which field to match against ('message', 'raw', 'source', or 'all')
        """
        self.include_patterns = [re.compile(p, re.IGNORECASE) for p in (include_patterns or [])]
        self.exclude_patterns = [re.compile(p, re.IGNORECASE) for p in (exclude_patterns or [])]
        self.field = field
    
    def should_include(self, entry: ParsedEntry) -> bool:
        # Check exclude patterns first (takes priority)
        if self.exclude_patterns:
            if self._matches(entry, self.exclude_patterns):
                return False
        
        # If no include patterns, include everything (unless excluded)
        if not self.include_patterns:
            return True
        
        # Check include patterns
        return self._matches(entry, self.include_patterns)
    
    def _matches(self, entry: ParsedEntry, patterns: List) -> bool:
        """Check if entry matches any of the patterns."""
        text_to_check = self._get_text(entry)
        return any(p.search(text_to_check) for p in patterns)
    
    def _get_text(self, entry: ParsedEntry) -> str:
        """Get text from entry based on field setting."""
        if self.field == 'all':
            parts = [entry.message, entry.raw, entry.source]
            if entry.metadata:
                parts.extend(str(v) for v in entry.metadata.values())
            return ' '.join(filter(None, parts))
        elif self.field == 'message':
            return entry.message
        elif self.field == 'raw':
            return entry.raw
        elif self.field == 'source':
            return entry.source
        return entry.raw
