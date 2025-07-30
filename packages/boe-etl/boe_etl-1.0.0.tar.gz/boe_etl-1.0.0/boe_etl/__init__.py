"""
BoE ETL Package
===============

A comprehensive ETL pipeline for financial document processing and NLP analysis.

This package provides tools for:
- Extracting data from PDFs, Excel files, and text documents
- Processing financial documents (earnings calls, reports, presentations)
- Converting unstructured data to structured NLP-ready formats
- Standardized taxonomy and naming conventions
- Web-based frontend for easy document processing

Main Components:
- parsers: Document parsing modules (PDF, Excel, Text, JSON)
- schema: Data transformation and standardization
- nlp: Natural language processing and feature extraction
- frontend: Streamlit-based web interface
- utils: Utility functions and helpers

Example Usage:
    >>> from boe_etl import ETLPipeline
    >>> pipeline = ETLPipeline()
    >>> results = pipeline.process_document('earnings_call.pdf', 'JPMorgan', 'Q1_2025')
    
    >>> from boe_etl.frontend import launch_frontend
    >>> launch_frontend()  # Starts web interface
"""

__version__ = "1.0.0"
__author__ = "Bank of England ETL Team"
__email__ = "etl-team@bankofengland.co.uk"

# Import main classes for easy access
try:
    from .core import ETLPipeline
    from .schema_transformer import SchemaTransformer
    from .parsers.pdf_parser import PDFParser
    from .parsers.excel_parser import ExcelParser
    from .parsers.text_parser import TextParser
    from .parsers.json_parser import JSONParser
    from .nlp import NLPProcessor
    
    __all__ = [
        'ETLPipeline',
        'SchemaTransformer', 
        'PDFParser',
        'ExcelParser',
        'TextParser',
        'JSONParser',
        'NLPProcessor',
        '__version__',
        '__author__',
        '__email__'
    ]
    
except ImportError as e:
    # Handle case where some modules might not be available
    import warnings
    warnings.warn(f"Some modules could not be imported: {e}")
    __all__ = ['__version__', '__author__', '__email__']

# Package metadata
PACKAGE_INFO = {
    'name': 'boe-etl',
    'version': __version__,
    'description': 'A comprehensive ETL pipeline for financial document processing and NLP analysis',
    'author': __author__,
    'email': __email__,
    'url': 'https://github.com/daleparr/boe-etl',
    'license': 'MIT',
    'keywords': ['etl', 'nlp', 'financial', 'banking', 'document-processing'],
}

def get_version():
    """Return the package version."""
    return __version__

def get_info():
    """Return package information."""
    return PACKAGE_INFO.copy()
