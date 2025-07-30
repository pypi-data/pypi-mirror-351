"""
Base parser interface for the ETL pipeline.

All parsers should implement the parse method that takes a file path
and returns a standardized data structure.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

class BaseParser(ABC):
    """Base class for all file parsers in the ETL pipeline."""
    
    def __init__(self, bank: str, quarter: str):
        """Initialize the parser with bank and quarter context.
        
        Args:
            bank: Name of the bank
            quarter: Quarter identifier (e.g., 'Q1_2025')
        """
        self.bank = bank
        self.quarter = quarter
    
    @abstractmethod
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse the given file and return structured data.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dictionary containing the parsed data
        """
        pass
    
    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic file metadata.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file metadata
        """
        stat = file_path.stat()
        return {
            'file_name': file_path.name,
            'file_size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'file_extension': file_path.suffix.lower(),
        }

# Example of how to implement a parser
class ExampleParser(BaseParser):
    """Example parser implementation."""
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse the file and return structured data."""
        # Implement parsing logic here
        result = {
            'bank': self.bank,
            'quarter': self.quarter,
            'file_path': str(file_path),
            'content': '',  # Add parsed content here
            'metadata': self.get_metadata(file_path)
        }
        
        # Add parsing logic here
        
        return result

def get_parser(file_extension: str, bank: str, quarter: str) -> Optional[BaseParser]:
    """Factory function to get the appropriate parser for a file extension.
    
    Args:
        file_extension: File extension including the dot (e.g., '.pdf')
        bank: Bank name
        quarter: Quarter identifier
        
    Returns:
        An instance of the appropriate parser, or None if no parser is available
    """
    from . import get_parser_class  # Import here to avoid circular imports
    
    parser_class = get_parser_class(file_extension.lower())
    if parser_class and issubclass(parser_class, BaseParser):
        return parser_class(bank, quarter)
    return None
