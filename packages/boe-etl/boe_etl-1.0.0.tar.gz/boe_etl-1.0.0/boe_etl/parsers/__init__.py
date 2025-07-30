"""
Parsers for different file types in the ETL pipeline.

This package provides functionality to parse various file types in a consistent way.
Each parser should implement the BaseParser interface or provide a function with
the signature (bank: str, quarter: str, file_path: Path, document_type: str = "unknown") -> Dict[str, Any].
"""
from pathlib import Path
from typing import Any, Dict, Optional, Type, Callable, Union

# Import parsers
from .base_parser import BaseParser, get_parser

# Import specific parser classes and functions
from .pdf_parser import PDFParser, parse_pdf
from .excel_parser import ExcelParser, parse_excel
from .json_parser import JSONParser, parse_json
from .text_parser import TextParser, parse_text

# Re-export public API
__all__ = [
    'BaseParser',
    'PDFParser',
    'ExcelParser',
    'JSONParser',
    'TextParser',
    'get_parser',
    'parse_pdf',
    'parse_excel',
    'parse_json',
    'parse_text',
]

# Dictionary mapping file extensions to parser classes
PARSER_CLASSES = {
    '.pdf': PDFParser,
    '.xlsx': ExcelParser,
    '.xls': ExcelParser,
    '.json': JSONParser,
    '.txt': TextParser,
}

# Dictionary mapping file extensions to parser functions (legacy support)
PARSERS = {
    '.pdf': parse_pdf,
    '.xlsx': parse_excel,
    '.xls': parse_excel,
    '.json': parse_json,
    '.txt': parse_text,
}

def get_parser_class(file_extension: str) -> Optional[Type[BaseParser]]:
    """Get the parser class for a file extension.
    
    Args:
        file_extension: File extension including the dot (e.g., '.pdf')
        
    Returns:
        Parser class if available, None otherwise
    """
    return PARSER_CLASSES.get(file_extension.lower())


def get_parser_func(file_extension: str) -> Optional[Callable[[str, str, Path, str], Dict[str, Any]]]:
    """Get the parser function for a file extension (legacy support).
    
    Args:
        file_extension: File extension including the dot (e.g., '.pdf')
        
    Returns:
        Parser function if available, None otherwise
    """
    return PARSERS.get(file_extension.lower())

def parse_file(bank: str, quarter: str, file_path: Path, document_type: str = "unknown") -> Dict[str, Any]:
    """Parse a file using the appropriate parser.
    
    Args:
        bank: Bank name
        quarter: Quarter identifier (e.g., 'Q1_2025')
        file_path: Path to the file to parse
        document_type: Type of document (e.g., 'transcript', 'presentation')
                     If "unknown", parsers will attempt to infer from filename
        
    Returns:
        Dictionary containing the parsed data
        
    Raises:
        ValueError: If no parser is available for the file type
    """
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_extension = file_path.suffix.lower()
    parser_func = get_parser_func(file_extension)
    
    if parser_func:
        return parser_func(bank, quarter, file_path, document_type)
    else:
        raise ValueError(f"No parser available for file type: {file_extension}")
