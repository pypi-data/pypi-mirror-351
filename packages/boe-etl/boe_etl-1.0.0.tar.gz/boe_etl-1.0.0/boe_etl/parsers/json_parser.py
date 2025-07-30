"""
JSON file parsing functionality for the ETL pipeline.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class JSONParser(BaseParser):
    """Parser for JSON files in the ETL pipeline."""
    
    def __init__(self, bank: str, quarter: str):
        """Initialize the JSON parser.
        
        Args:
            bank: Name of the bank
            quarter: Quarter identifier (e.g., 'Q1_2025')
        """
        super().__init__(bank, quarter)
        self.supported_formats = {'.json'}
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse a JSON file and extract its content.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary containing the parsed data with standardized structure
        """
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        # Infer document type from filename
        document_type = self._infer_document_type(file_path.name)
        
        result = {
            'bank': self.bank,
            'quarter': self.quarter,
            'file_path': str(file_path),
            'document_type': document_type,
            'content': '',
            'metadata': self.get_metadata(file_path),
            'data': {}
        }
        
        try:
            # Read the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Store the raw data
            result['data'] = data
            
            # Extract bank name from data if available
            if isinstance(data, dict) and 'bank' in data:
                result['bank'] = data['bank']
                
            # Extract quarter from data if available
            if isinstance(data, dict) and 'quarter' in data:
                result['quarter'] = data['quarter']
                
            # Process based on document type
            if document_type == "transcript" and isinstance(data, dict) and 'transcript' in data:
                # Handle transcript data
                result['content'] = "\n\n".join(
                    f"{item.get('speaker', 'Unknown')}: {item.get('text', '')}"
                    for item in data['transcript']
                    if isinstance(item, dict)
                )
            else:
                # Generic JSON content representation
                result['content'] = json.dumps(data, indent=2)
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing JSON file {file_path}: {str(e)}")
            raise
    
    def _infer_document_type(self, filename: str) -> str:
        """Infer the document type from the filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            Inferred document type
        """
        filename = filename.lower()
        if "transcript" in filename:
            return "transcript"
        elif "data" in filename:
            return "data"
        elif any(term in filename for term in ["result", "financial"]):
            return "results"
        return "other"

def parse_json(bank: str, quarter: str, file_path: Path, document_type: str = "unknown") -> Dict[str, Any]:
    """
    Parse a JSON file and extract its content.
    
    This is a convenience function that creates a JSONParser instance.
    For new code, it's recommended to use the JSONParser class directly.
    
    Args:
        bank: Name of the bank
        quarter: Quarter identifier (e.g., 'Q1_2025')
        file_path: Path to the JSON file
        document_type: Type of document (e.g., 'transcript', 'data')
               If "unknown", will attempt to infer from filename
    
    Returns:
        Dictionary containing the parsed data
    """
    parser = JSONParser(bank, quarter)
    result = parser.parse(file_path)
    
    # For backward compatibility
    if document_type != "unknown" and document_type != result['document_type']:
        result['document_type'] = document_type
        
    return result

def test_parse_json():
    """Test function for the JSON parser"""
    import tempfile
    from pathlib import Path
    
    # Create a simple JSON file for testing
    test_data = {
        "bank": "TestBank",
        "quarter": "Q1_2025",
        "transcript": [
            {"speaker": "CEO", "text": "Welcome to our quarterly earnings call."},
            {"speaker": "CFO", "text": "Our financial results this quarter have been strong."}
        ]
    }
    
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        with open(tmp.name, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        
        test_file = Path(tmp.name)
    
    try:
        parser = JSONParser('test_bank', 'Q1_2025')
        result = parser.parse(test_file)
        print("JSON parse test successful!")
        print(f"Bank: {result['bank']}")
        print(f"Document type: {result['document_type']}")
        print(f"Content: {result['content'][:50]}...")
        return True
    except Exception as e:
        print(f"JSON parse test failed: {str(e)}")
        return False
    finally:
        test_file.unlink()  # Clean up

if __name__ == "__main__":
    test_parse_json()