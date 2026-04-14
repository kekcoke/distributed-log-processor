"""Log parsers for various log formats."""
from .base import BaseParser, ParsedEntry
from .plain_text import PlainTextParser
from .json_parser import JSONParser
from .windows_event import WindowsEventParser
from .ce_parser import CEParser
from .clf_parser import CLFParser
from .elf_parser import ELFParser
from .w3c_parser import W3CParser

PARSERS = {
    'plaintext': PlainTextParser,
    'json': JSONParser,
    'windows_event': WindowsEventParser,
    'ce': CEParser,
    'clf': CLFParser,
    'elf': ELFParser,
    'w3c': W3CParser,
}


def get_parser(format_type: str) -> BaseParser:
    """Factory function to get a parser by format type."""
    parser_class = PARSERS.get(format_type.lower())
    if not parser_class:
        raise ValueError(f"Unknown parser format: {format_type}")
    return parser_class()


def auto_detect_format(sample_line: str) -> str:
    """Auto-detect log format from a sample line."""
    sample = sample_line.strip()
    if not sample:
        return 'plaintext'
    
    # JSON detection
    if sample.startswith('{') and sample.endswith('}'):
        try:
            import json
            json.loads(sample)
            return 'json'
        except:
            pass
    
    # Windows Event (XML-like)
    if '<Event xmlns=' in sample or '<Event>' in sample:
        return 'windows_event'
    
    # CE (Cisco Erase) - timestamp + severity + message
    if '%' in sample and ('-' in sample[:30]):
        return 'ce'
    
    # CLF (Common Log Format) - IP - - [timestamp] "method url protocol" status size
    if '[' in sample and '"' in sample and ' - - ' in sample:
        return 'clf'
    
    # ELF (Extended Log Format) - tab/space separated fields
    if '\t' in sample and not sample.startswith('#'):
        return 'elf'
    
    # W3C Extended Log Format - fields start with #Fields
    if sample.startswith('#'):
        return 'w3c'
    
    return 'plaintext'
