"""Base tagger class for log categorization."""
from abc import ABC, abstractmethod
from typing import List, Set
from parsers.base import ParsedEntry


class BaseTagger(ABC):
    """Abstract base class for log taggers."""
    
    @abstractmethod
    def tag(self, entry: ParsedEntry) -> Set[str]:
        """Return a set of tags for the entry."""
        return set()
    
    def tag_entry(self, entry: ParsedEntry) -> ParsedEntry:
        """Add tags to an entry and return it."""
        tags = self.tag(entry)
        if tags:
            if not hasattr(entry, 'tags'):
                entry.metadata['tags'] = set()
            entry.metadata['tags'].update(tags)
        return entry
