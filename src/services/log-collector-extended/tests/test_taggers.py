"""Tests for log taggers."""
import pytest
from parsers.base import ParsedEntry
from taggers.rule_tagger import RuleTagger
from taggers.keyword_tagger import KeywordTagger


def make_entry(message="Test message", level="INFO"):
    return ParsedEntry(message=message, level=level, raw=message, format_type="plaintext")


class TestRuleTagger:
    def test_tag_with_rules(self):
        tagger = RuleTagger({
            'security': ['failed.*login', 'unauthorized'],
            'database': ['query', 'sql'],
        })
        
        entry = make_entry("Failed login attempt")
        tags = tagger.tag(entry)
        
        assert 'security' in tags
        assert 'database' not in tags
    
    def test_multiple_tags(self):
        tagger = RuleTagger({
            'error': ['error', 'fail'],
            'auth': ['login', 'auth'],
        })
        
        entry = make_entry("Authentication error")
        tags = tagger.tag(entry)
        
        assert 'error' in tags
        assert 'auth' in tags
    
    def test_case_insensitive(self):
        tagger = RuleTagger({
            'security': ['UNAUTHORIZED'],
        })
        
        entry = make_entry("unauthorized access")
        tags = tagger.tag(entry)
        
        assert 'security' in tags


class TestKeywordTagger:
    def test_keyword_matching(self):
        tagger = KeywordTagger({
            'api': ['api', 'rest', 'endpoint'],
            'network': ['connection', 'timeout'],
        })
        
        entry = make_entry("API connection timeout")
        tags = tagger.tag(entry)
        
        assert 'api' in tags
        assert 'network' in tags
    
    def test_case_insensitive(self):
        tagger = KeywordTagger({
            'error': ['error'],
        })
        
        entry = make_entry("ERROR occurred")
        tags = tagger.tag(entry)
        
        assert 'error' in tags
    
    def test_no_match(self):
        tagger = KeywordTagger({
            'api': ['api'],
        })
        
        entry = make_entry("Database query executed")
        tags = tagger.tag(entry)
        
        assert len(tags) == 0


class TestTaggerIntegration:
    def test_add_rule(self):
        tagger = RuleTagger()
        tagger.add_rule('security', ['hack', 'breach'])
        
        entry = make_entry("Security breach detected")
        tags = tagger.tag(entry)
        
        assert 'security' in tags
    
    def test_add_keywords(self):
        tagger = KeywordTagger()
        tagger.add_keywords('database', ['sql', 'query'])
        
        entry = make_entry("SQL query slow")
        tags = tagger.tag(entry)
        
        assert 'database' in tags
