"""Log taggers for categorizing log entries."""
from .base import BaseTagger
from .rule_tagger import RuleTagger
from .keyword_tagger import KeywordTagger

__all__ = ['BaseTagger', 'RuleTagger', 'KeywordTagger']
