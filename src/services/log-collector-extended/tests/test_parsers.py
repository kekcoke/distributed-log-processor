"""Tests for log parsers."""
import pytest
from parsers.base import ParsedEntry
from parsers import get_parser, auto_detect_format, PARSERS
from parsers.plain_text import PlainTextParser
from parsers.json_parser import JSONParser
from parsers.windows_event import WindowsEventParser
from parsers.ce_parser import CEParser
from parsers.clf_parser import CLFParser
from parsers.elf_parser import ELFParser
from parsers.w3c_parser import W3CParser


class TestPlainTextParser:
    def test_parse_iso_timestamp_with_level(self):
        parser = PlainTextParser()
        entry = parser.parse("2024-01-15 10:30:45 [INFO] User logged in")
        
        assert entry is not None
        assert entry.level == "INFO"
        assert "logged in" in entry.message
        assert entry.format_type == "plaintext"
    
    def test_parse_error_level(self):
        parser = PlainTextParser()
        entry = parser.parse("2024-01-15 10:30:45 ERROR Failed to connect")
        
        assert entry is not None
        assert entry.level == "ERROR"
    
    def test_parse_unstructured(self):
        parser = PlainTextParser()
        entry = parser.parse("Some random log message")
        
        assert entry is not None
        assert entry.message == "Some random log message"
    
    def test_parse_empty_line(self):
        parser = PlainTextParser()
        entry = parser.parse("")
        
        assert entry is None


class TestJSONParser:
    def test_parse_json_entry(self):
        parser = JSONParser()
        line = '{"timestamp": "2024-01-15T10:30:45", "level": "ERROR", "message": "Failed"}'
        entry = parser.parse(line)
        
        assert entry is not None
        assert entry.level == "ERROR"
        assert "Failed" in entry.message
        assert entry.format_type == "json"
    
    def test_parse_invalid_json(self):
        parser = JSONParser()
        entry = parser.parse("not valid json")
        
        assert entry is None
    
    def test_parse_json_with_metadata(self):
        parser = JSONParser()
        line = '{"timestamp": "2024-01-15T10:30:45", "level": "INFO", "message": "Test", "user_id": 123}'
        entry = parser.parse(line)
        
        assert entry is not None
        assert entry.metadata.get("user_id") == 123


class TestWindowsEventParser:
    def test_parse_windows_event(self):
        parser = WindowsEventParser()
        line = '<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event"><System><Provider Name="Test"/><EventID>100</EventID><Level>2</Level><TimeCreated SystemTime="2024-01-15T10:30:45Z"/><Computer>DC01</Computer></System><EventData><Message>Test message</Message></EventData></Event>'
        entry = parser.parse(line)
        
        assert entry is not None
        assert entry.level == "ERROR"  # Level 2 = Error
        assert entry.metadata.get("event_id") == 100
        assert entry.format_type == "windows_event"


class TestCEParser:
    def test_parse_cisco_syslog(self):
        parser = CEParser()
        line = "Jan 15 10:30:45 router01 %SYS-5-CONFIG_I: Configuration saved"
        entry = parser.parse(line)
        
        assert entry is not None
        assert entry.level == "NOTICE"  # Severity 5 = Notice
        assert entry.metadata.get("facility") == "SYS"


class TestCLFParser:
    def test_parse_clf_entry(self):
        parser = CLFParser()
        line = '127.0.0.1 - - [15/Jan/2024:10:30:45 -0700] "GET /api/users HTTP/1.1" 200 1234'
        entry = parser.parse(line)
        
        assert entry is not None
        assert entry.metadata.get("status") == 200
        assert entry.metadata.get("method") == "GET"
        assert entry.format_type == "clf"
    
    def test_parse_clf_error_status(self):
        parser = CLFParser()
        line = '127.0.0.1 - - [15/Jan/2024:10:30:45 -0700] "GET /api/error HTTP/1.1" 500 0'
        entry = parser.parse(line)
        
        assert entry is not None
        assert entry.level == "ERROR"
    
    def test_parse_clf_unauthorized(self):
        parser = CLFParser()
        line = '127.0.0.1 - - [15/Jan/2024:10:30:45 -0700] "POST /login HTTP/1.1" 401 256'
        entry = parser.parse(line)
        
        assert entry is not None
        assert entry.level == "WARNING"


class TestELFParser:
    def test_parse_elf_entry(self):
        parser = ELFParser()
        line = "2024-01-15\t10:30:45\t192.168.1.1\t10.0.0.1\t80\tGET\t/api\t200"
        entry = parser.parse(line)
        
        assert entry is not None
        assert entry.metadata.get("method") == "GET"


class TestW3CParser:
    def test_parse_w3c_header(self):
        parser = W3CParser()
        line = "#Fields: date time c-ip s-ip s-port cs-method cs-uri sc-status"
        entry = parser.parse(line)
        
        # Header lines return None (no entry)
        assert entry is None
        assert len(parser.fields) > 0
    
    def test_parse_w3c_entry(self):
        parser = W3CParser()
        # First set the fields
        parser.fields = ['date', 'time', 'c-ip', 's-ip', 's-port', 'cs-method', 'cs-uri', 'sc-status']
        parser.field_map = {name: idx for idx, name in enumerate(parser.fields)}
        
        line = "2024-01-15 10:30:45 192.168.1.1 10.0.0.1 80 GET /api 200"
        entry = parser.parse(line)
        
        assert entry is not None
        assert entry.metadata.get("method") == "GET"
        assert entry.metadata.get("status") == 200


class TestParserFactory:
    def test_get_parser(self):
        parser = get_parser("json")
        assert isinstance(parser, JSONParser)
    
    def test_get_unknown_parser(self):
        with pytest.raises(ValueError):
            get_parser("unknown_format")
    
    def test_auto_detect_json(self):
        format_type = auto_detect_format('{"key": "value"}')
        assert format_type == "json"
    
    def test_auto_detect_plaintext(self):
        format_type = auto_detect_format("2024-01-15 10:30:45 INFO Message")
        assert format_type == "plaintext"
    
    def test_auto_detect_clf(self):
        format_type = auto_detect_format('127.0.0.1 - - [15/Jan/2024:10:30:45] "GET / HTTP/1.1" 200 0')
        assert format_type == "clf"


class TestParsedEntry:
    def test_to_dict(self):
        from datetime import datetime
        entry = ParsedEntry(
            timestamp=datetime(2024, 1, 15, 10, 30, 45),
            level="INFO",
            message="Test message",
            source="test",
            raw="raw line",
            format_type="plaintext"
        )
        d = entry.to_dict()
        
        assert d["level"] == "INFO"
        assert d["message"] == "Test message"
        assert d["timestamp"] is not None
