"""Keyword-based tagger for log categorization."""
from typing import Dict, Set
from .base import BaseTagger
from parsers.base import ParsedEntry


class KeywordTagger(BaseTagger):
    """Tag entries based on keyword/phrase matching."""
    
    def __init__(self, keywords: Dict[str, list] = None):
        """
        Args:
            keywords: Dict of tag -> list of keywords/phrases
                     e.g., {'security': ['login', 'auth', 'token'], 'database': ['query', 'sql', 'connection']}
        """
        self.keywords = keywords or {}
        # Convert to lowercase for case-insensitive matching
        self.keywords = {tag: [k.lower() for k in words] for tag, words in self.keywords.items()}
    
    def add_keywords(self, tag: str, keywords: list):
        """Add keywords to a tag."""
        if tag not in self.keywords:
            self.keywords[tag] = []
        self.keywords[tag].extend([k.lower() for k in keywords])
    
    def tag(self, entry: ParsedEntry) -> Set[str]:
        """Match keywords and return tags."""
        tags = set()
        text = self._get_text(entry).lower()
        
        for tag, words in self.keywords.items():
            if any(word in text for word in words):
                tags.add(tag)
        
        return tags
    
    def _get_text(self, entry: ParsedEntry) -> str:
        """Combine relevant fields for matching."""
        parts = [entry.message, entry.raw]
        if entry.level:
            parts.append(entry.level)
        parts.extend(str(v) for v in entry.metadata.values() if isinstance(v, str))
        return ' '.join(parts)
