"""Tests for log filters."""
import pytest
from parsers.base import ParsedEntry
from filters.base import BaseFilter
from filters.regex_filter import RegexFilter
from filters.level_filter import LevelFilter
from filters.composite_filter import CompositeFilter


def make_entry(level="INFO", message="Test message", raw="raw"):
    return ParsedEntry(level=level, message=message, raw=raw, format_type="plaintext")


class TestLevelFilter:
    def test_include_specific_levels(self):
        filter_obj = LevelFilter(include_levels=["ERROR", "CRITICAL"])
        
        assert not filter_obj.should_include(make_entry("INFO"))
        assert not filter_obj.should_include(make_entry("DEBUG"))
        assert filter_obj.should_include(make_entry("ERROR"))
        assert filter_obj.should_include(make_entry("CRITICAL"))
    
    def test_exclude_levels(self):
        filter_obj = LevelFilter(exclude_levels=["DEBUG", "INFO"])
        
        assert not filter_obj.should_include(make_entry("DEBUG"))
        assert not filter_obj.should_include(make_entry("INFO"))
        assert filter_obj.should_include(make_entry("WARNING"))
        assert filter_obj.should_include(make_entry("ERROR"))
    
    def test_min_level(self):
        filter_obj = LevelFilter(min_level="WARNING")
        
        assert not filter_obj.should_include(make_entry("DEBUG"))
        assert not filter_obj.should_include(make_entry("INFO"))
        assert filter_obj.should_include(make_entry("WARNING"))
        assert filter_obj.should_include(make_entry("ERROR"))
        assert filter_obj.should_include(make_entry("CRITICAL"))


class TestRegexFilter:
    def test_include_pattern(self):
        filter_obj = RegexFilter(include_patterns=["error", "failed"])
        
        assert not filter_obj.should_include(make_entry(message="Success"))
        assert filter_obj.should_include(make_entry(message="An error occurred"))
        assert filter_obj.should_include(make_entry(message="Connection failed"))
    
    def test_exclude_pattern(self):
        filter_obj = RegexFilter(exclude_patterns=["heartbeat", "health"])
        
        assert filter_obj.should_include(make_entry(message="Error occurred"))
        assert not filter_obj.should_include(make_entry(message="heartbeat check"))
    
    def test_exclude_takes_priority(self):
        # Even if include matches, exclude should filter out
        filter_obj = RegexFilter(
            include_patterns=["error"],
            exclude_patterns=["timeout.*error"]
        )
        
        assert filter_obj.should_include(make_entry(message="General error"))
        assert not filter_obj.should_include(make_entry(message="timeout error"))
    
    def test_empty_filters(self):
        filter_obj = RegexFilter()
        assert filter_obj.should_include(make_entry())


class TestCompositeFilter:
    def test_and_mode_all_pass(self):
        f1 = LevelFilter(include_levels=["ERROR"])
        f2 = RegexFilter(include_patterns=["database"])
        
        composite = CompositeFilter([f1, f2], mode="AND")
        
        assert not composite.should_include(make_entry("INFO", "database error"))
        assert not composite.should_include(make_entry("ERROR", "api error"))
        assert composite.should_include(make_entry("ERROR", "database error"))
    
    def test_or_mode_one_passes(self):
        f1 = LevelFilter(include_levels=["ERROR"])
        f2 = RegexFilter(include_patterns=["database"])
        
        composite = CompositeFilter([f1, f2], mode="OR")
        
        assert not composite.should_include(make_entry("INFO", "api request"))
        assert composite.should_include(make_entry("INFO", "database query"))
        assert composite.should_include(make_entry("ERROR", "api error"))
    
    def test_add_filter(self):
        composite = CompositeFilter()
        composite.add_filter(LevelFilter(include_levels=["ERROR"]))
        
        assert len(composite.filters) == 1
        assert not composite.should_include(make_entry("INFO"))
