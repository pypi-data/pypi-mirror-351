"""
PDF parsing functionality for the ETL pipeline.
"""
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Third-party imports
try:
    import PyPDF2
    import pdfplumber
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer, LTChar, LTTextLineHorizontal
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    PyPDF2 = None
    pdfplumber = None
    extract_pages = None
    LTTextContainer = None

from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """Parser for PDF files in the ETL pipeline."""
    
    def __init__(self, bank: str, quarter: str):
        """Initialize the PDF parser.
        
        Args:
            bank: Name of the bank
            quarter: Quarter identifier (e.g., 'Q1_2025')
        """
        super().__init__(bank, quarter)
        self.supported_formats = {'.pdf'}
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse a PDF file and extract its content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing the parsed data with standardized structure
        """
        if not PDF_SUPPORT:
            raise ImportError("PDF parsing requires PyPDF2 and pdfplumber packages.")
            
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Infer document type from filename
        document_type = self._infer_document_type(file_path.name)
        
        result = {
            'bank': self.bank,
            'quarter': self.quarter,
            'file_path': str(file_path),
            'document_type': document_type,
            'content': {
                'pages': [],
                'metadata': {}
            },
            'metadata': self.get_metadata(file_path)
        }
        
        try:
            # Extract text and metadata
            self._extract_text_and_metadata(file_path, result['content'])
            
            # Extract additional structural information
            self._extract_structure(file_path, result['content'])
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path}: {str(e)}")
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
        elif "presentation" in filename or "prqtr" in filename:
            return "presentation"
        elif "supplement" in filename or "fsqtr" in filename:
            return "supplement"
        elif "result" in filename or "rslt" in filename:
            return "results"
        return "other"
    
    def _extract_text_and_metadata(self, file_path: Path, content: Dict):
        """Extract text and metadata from the PDF."""
        with pdfplumber.open(file_path) as pdf:
            # Extract metadata
            content['metadata'].update({
                'page_count': len(pdf.pages),
                'author': pdf.metadata.get('Author'),
                'creator': pdf.metadata.get('Creator'),
                'producer': pdf.metadata.get('Producer'),
                'created': pdf.metadata.get('CreationDate'),
                'modified': pdf.metadata.get('ModDate'),
            })
            
            # Extract text from each page
            for i, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    content['pages'].append({
                        'page_number': i + 1,
                        'text': page_text,
                        'dimensions': {
                            'width': page.width,
                            'height': page.height
                        },
                        'metadata': {
                            'has_tables': len(page.extract_tables()) > 0
                        }
                    })
                except Exception as e:
                    logger.warning(f"Error extracting text from page {i+1}: {str(e)}")
                    content['pages'].append({
                        'page_number': i + 1,
                        'error': str(e)
                    })
    
    def _extract_structure(self, file_path: Path, content: Dict):
        """Extract structural information from the PDF."""
        if not extract_pages:
            logger.warning("PDFMiner not available, skipping structure extraction")
            return
        
        try:
            # Extract text with layout information
            for i, page_layout in enumerate(extract_pages(file_path)):
                if i >= len(content['pages']):
                    break
                    
                page_content = content['pages'][i]
                if 'error' in page_content:
                    continue
                    
                # Extract text elements with their positions
                text_elements = []
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        # Get the text and its bounding box
                        text = element.get_text().strip()
                        if not text:
                            continue
                            
                        # Get font information
                        font_info = {}
                        for text_line in element:
                            if isinstance(text_line, LTTextLineHorizontal):
                                for char in text_line:
                                    if hasattr(char, 'fontname') and hasattr(char, 'size'):
                                        font_info = {
                                            'font_name': char.fontname,
                                            'font_size': char.size,
                                            'bold': 'bold' in char.fontname.lower() if char.fontname else False,
                                            'italic': 'italic' in char.fontname.lower() if char.fontname else False
                                        }
                                        break
                                if font_info:
                                    break
                        
                        text_elements.append({
                            'text': text,
                            'bbox': {
                                'x0': element.x0,
                                'y0': element.y0,
                                'x1': element.x1,
                                'y1': element.y1,
                                'width': element.width,
                                'height': element.height
                            },
                            'font': font_info
                        })
                
                page_content['elements'] = text_elements
                
        except Exception as e:
            logger.warning(f"Error extracting PDF structure: {str(e)}")
            # Don't fail the whole process if structure extraction fails
            pass

def parse_pdf(bank: str, quarter: str, file_path: Path, document_type: str = "unknown") -> Dict[str, Any]:
    """
    Parse a PDF file and extract its content.
    
    Args:
        bank: Name of the bank
        quarter: Quarter identifier (e.g., 'Q1_2025')
        file_path: Path to the PDF file
        document_type: Type of document (e.g., 'transcript', 'presentation', 'supplement')
                     If "unknown", will attempt to infer from filename
    
    Returns:
        Dictionary containing the parsed data
    """
    # Infer document type from filename if not provided
    if document_type == "unknown":
        file_name = file_path.name.lower()
        if "transcript" in file_name:
            document_type = "transcript"
        elif "presentation" in file_name or "prqtr" in file_name:
            document_type = "presentation"
        elif "supplement" in file_name or "fsqtr" in file_name:
            document_type = "supplement"
        elif "result" in file_name or "rslt" in file_name:
            document_type = "results"
        else:
            document_type = "other"
            
    logger.info(f"Document type determined as: {document_type}")
    if not PDF_SUPPORT:
        raise ImportError("PDF parsing requires PyPDF2 and pdfplumber packages.")
    
    logger.info(f"Parsing PDF: {file_path}")
    
    # Initialize result dictionary
    result = {
        'bank': bank,
        'quarter': quarter,
        'file_path': str(file_path),
        'document_type': document_type,
        'content': '',
        'metadata': {},
        'pages': []
    }
    
    try:
        # Extract metadata using PyPDF2
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            # Get document info
            if pdf_reader.metadata:
                result['metadata'].update({
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                    'producer': pdf_reader.metadata.get('/Producer', ''),
                    'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                    'modification_date': pdf_reader.metadata.get('/ModDate', '')
                })
            
            # Extract text from each page using pdfplumber (better text extraction)
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            result['pages'].append({
                                'page_number': i + 1,
                                'text': page_text.strip()
                            })
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {i+1}: {str(e)}")
            
            # Combine all page texts
            result['content'] = '\n\n'.join(page['text'] for page in result['pages'])
            
            # Add page count
            result['metadata']['page_count'] = len(pdf_reader.pages)
            
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {str(e)}")
        raise
    
    return result

# Add a simple test function for the parser
def test_parse_pdf():
    """Test function for the PDF parser"""
    import tempfile
    from pathlib import Path
    
    # Create a simple PDF for testing
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        pdf_writer = PyPDF2.PdfWriter()
        page = PyPDF2.PageObject.create_blank_page(width=72, height=72)
        page.merge_page(PyPDF2.PageObject.create_blank_page(width=72, height=72))
        pdf_writer.add_page(page)
        with open(tmp.name, 'wb') as f:
            pdf_writer.write(f)
        
        test_file = Path(tmp.name)
    
    try:
        result = parse_pdf('test_bank', 'Q1_2025', test_file, 'test_document')
        print("PDF parse test successful!")
        print(f"Pages: {len(result['pages'])}")
        print(f"Document type: {result['document_type']}")
        return True
    except Exception as e:
        print(f"PDF parse test failed: {str(e)}")
        return False
    finally:
        test_file.unlink()  # Clean up

if __name__ == "__main__":
    if PDF_SUPPORT:
        test_parse_pdf()
    else:
        print("PDF parsing dependencies not installed. Skipping test.")
