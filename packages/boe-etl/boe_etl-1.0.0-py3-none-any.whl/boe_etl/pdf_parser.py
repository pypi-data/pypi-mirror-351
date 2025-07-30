import pdfplumber
import re
from typing import Dict, List, Any, Optional, Union
import logging
from pathlib import Path
from datetime import datetime
from .error_handling import get_exception_handler
from .config import ConfigManager

class PDFParser:
    """Parser for PDF documents"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.error_handler = get_exception_handler()
        
    def parse_pdf(self, file_path: str, document_type: str) -> List[Dict]:
        """
        Parse a PDF or text document
        Args:
            file_path: Path to the file
            document_type: Type of document (presentation/transcript/supplement/results/other)
        Returns:
            List of parsed records
        """
        try:
            # Determine file type by extension
            if file_path.lower().endswith('.pdf'):
                return self._parse_pdf_file(file_path, document_type)
            elif file_path.lower().endswith('.txt'):
                return self._parse_text_file(file_path, document_type)
            else:
                raise ValueError(f"Unsupported file type: {file_path}")
                
        except Exception as e:
            # Extract bank and quarter from path for more accurate error reporting
            path_parts = Path(file_path).parts
            bank_name = "unknown"
            quarter = "unknown"
            
            # Try to find bank and quarter in the path
            for part in path_parts:
                if part in ["Citigroup", "JPMorgan", "BankOfAmerica"]:
                    bank_name = part
                elif part.startswith("Q") and ("_" in part or " " in part):
                    quarter = part
                    
            self.error_handler.handle_error(
                e,
                bank_name,
                quarter,
                "file_parsing",
                {"file": file_path}
            )
            return []
    
    def _parse_pdf_file(self, pdf_path: str, document_type: str) -> List[Dict]:
        """Parse a PDF file"""
        records = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    continue
                
                # Clean extracted text
                text = self._clean_text(text)
                
                # Split into paragraphs
                paragraphs = self._split_into_paragraphs(text)
                
                for para in paragraphs:
                    record = {
                        "text": para,
                        "page_number": page_num,
                        "document_type": document_type,
                        "source_file": pdf_path,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Add document-specific metadata
                    if document_type == "transcript":
                        record.update(self._extract_speaker_info(para))
                    elif document_type == "presentation":
                        record.update(self._extract_slide_info(page))
                    
                    records.append(record)
        
        return records
    
    def _parse_text_file(self, text_path: str, document_type: str) -> List[Dict]:
        """Parse a text file"""
        records = []
        
        try:
            with open(text_path, 'r') as f:
                text = f.read()
                
            # Split into paragraphs
            paragraphs = [p for p in text.split('\n\n') if p.strip()]
            
            for para_num, para in enumerate(paragraphs, 1):
                record = {
                    "text": para,
                    "page_number": 1,  # All in one page
                    "document_type": document_type,
                    "source_file": text_path,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add document-specific metadata
                if document_type == "transcript":
                    record.update(self._extract_speaker_info(para))
                elif document_type == "presentation":
                    # For text files, don't try to use page object
                    record["slide_title"] = "unknown"
                
                records.append(record)
            
            return records
            
        except Exception as e:
            # Extract path components for better error reporting
            path_parts = Path(text_path).parts
            bank_name = "unknown"
            quarter = "unknown"
            
            for part in path_parts:
                if part in ["Citigroup", "JPMorgan", "BankOfAmerica"]:
                    bank_name = part
                elif part.startswith("Q"):
                    quarter = part
            
            self.error_handler.handle_error(
                e,
                bank_name,
                quarter,
                "text_parsing",
                {"file": text_path}
            )
            return []
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove page headers/footers
        text = re.sub(r"\d+ of \d+", "", text)
        # Remove multiple spaces
        text = re.sub(r"\s+", " ", text)
        # Remove page numbers
        text = re.sub(r"^\d+$", "", text)
        return text.strip()
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split by double newlines
        paragraphs = text.split('\n\n')
        # Filter out empty paragraphs
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _extract_speaker_info(self, text: str) -> Dict:
        """Extract speaker information from transcript"""
        # Simple speaker extraction (can be enhanced)
        speaker_match = re.match(r"^(.*?):\s+(.*)", text)
        if speaker_match:
            return {
                "speaker": speaker_match.group(1),
                "text": speaker_match.group(2)
            }
        return {"speaker": "unknown", "text": text}
    
    def _extract_slide_info(self, page) -> Dict:
        """Extract slide information from presentation"""
        # Extract slide title (first line)
        text = page.extract_text()
        if text:
            first_line = text.split('\n')[0].strip()
            return {"slide_title": first_line}
        return {"slide_title": "unknown"}

def get_pdf_parser() -> PDFParser:
    """Get the singleton PDF parser instance"""
    if not hasattr(get_pdf_parser, 'instance'):
        get_pdf_parser.instance = PDFParser()
    return get_pdf_parser.instance
