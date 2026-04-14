"""Rule-based tagger for log categorization."""
import re
from typing import Dict, List, Set
from .base import BaseTagger
from parsers.base import ParsedEntry


class RuleTagger(BaseTagger):
    """Tag entries based on configurable rules."""
    
    def __init__(self, rules: Dict[str, List[str]] = None):
        """
        Args:
            rules: Dict of tag -> list of regex patterns
                   e.g., {'security': ['failed.*login', 'unauthorized'], 'error': ['error', 'exception']}
        """
        self.rules = {}
        if rules:
            for tag, patterns in rules.items():
                self.rules[tag] = [re.compile(p, re.IGNORECASE) for p in patterns]
    
    def add_rule(self, tag: str, patterns: List[str]):
        """Add a tagging rule."""
        if tag not in self.rules:
            self.rules[tag] = []
        self.rules[tag].extend([re.compile(p, re.IGNORECASE) for p in patterns])
    
    def tag(self, entry: ParsedEntry) -> Set[str]:
        """Apply rules and return matching tags."""
        tags = set()
        text = self._get_text(entry)
        
        for tag, patterns in self.rules.items():
            if any(p.search(text) for p in patterns):
                tags.add(tag)
        
        return tags
    
    def _get_text(self, entry: ParsedEntry) -> str:
        """Combine relevant fields for matching."""
        parts = [entry.message, entry.raw]
        if entry.level:
            parts.append(entry.level)
        if entry.source:
            parts.append(entry.source)
        parts.extend(str(v) for v in entry.metadata.values() if isinstance(v, str))
        return ' '.join(parts)
