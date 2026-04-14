"""Tests for log writers."""
import json
import os
import pytest
import tempfile
from parsers.base import ParsedEntry
from writers.json_writer import JSONWriter
from writers.csv_writer import CSVWriter
from writers.ndjson_writer import NDJSONWriter


def make_entry(message="Test", level="INFO"):
    return ParsedEntry(message=message, level=level, raw=message, format_type="plaintext")


class TestJSONWriter:
    def test_write_single_entry(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            writer = JSONWriter(path)
            writer.write([make_entry("Test message")])
            
            with open(path) as f:
                data = json.load(f)
            
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]['message'] == "Test message"
        finally:
            os.unlink(path)
    
    def test_append_entries(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            writer = JSONWriter(path)
            writer.write([make_entry("First")])
            writer.write([make_entry("Second")])
            
            with open(path) as f:
                data = json.load(f)
            
            assert len(data) == 2
        finally:
            os.unlink(path)


class TestCSVWriter:
    def test_write_entry(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            path = f.name
        
        try:
            writer = CSVWriter(path)
            writer.write([make_entry("CSV Test", "ERROR")])
            
            with open(path) as f:
                lines = f.readlines()
            
            assert len(lines) == 2  # Header + 1 entry
            assert "CSV Test" in lines[1]
            assert "ERROR" in lines[1]
        finally:
            os.unlink(path)


class TestNDJSONWriter:
    def test_write_entries(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            path = f.name
        
        try:
            writer = NDJSONWriter(path)
            writer.write([make_entry("Line 1"), make_entry("Line 2")])
            
            with open(path) as f:
                lines = f.readlines()
            
            assert len(lines) == 2
            for line in lines:
                data = json.loads(line)
                assert 'message' in data
        finally:
            os.unlink(path)
    
    def test_append_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            path = f.name
        
        try:
            writer = NDJSONWriter(path)
            writer.write([make_entry("Original")])
            writer.write([make_entry("Appended")])
            
            with open(path) as f:
                lines = f.readlines()
            
            assert len(lines) == 2
        finally:
            os.unlink(path)
