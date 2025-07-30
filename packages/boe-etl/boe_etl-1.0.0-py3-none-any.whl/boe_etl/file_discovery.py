"""
File discovery and processing for the ETL pipeline.

This module provides functionality to discover and process files in a directory structure,
with flexible organization that doesn't rely on specific naming conventions.
"""
import logging
import re
import os
from pathlib import Path
from typing import Dict, Callable, Optional, List, TypeVar, Any, Tuple
from functools import partial

# Type variable for the parser function
T = TypeVar('T')

# Configure logger
logger = logging.getLogger(__name__)

# Default supported file extensions and their parsers
DEFAULT_PARSERS = {
    '.pdf': None,  # Will be set to parse_pdf if available
    '.html': None,  # Will be set to parse_html if available
    '.htm': None,   # Alias for .html
    '.vtt': None,   # Will be set to parse_vtt if available
    '.csv': None,   # Will be set to parse_csv if available
    '.xlsx': None,  # Will be set to parse_excel if available
    '.xls': None,   # Alias for .xlsx
    '.txt': None,   # Will be set to parse_text if available
    '.json': None,  # Will be set to parse_json if available
}

# Document type inference patterns
DOCUMENT_TYPE_PATTERNS = {
    'transcript': [r'transcript', r'call', r'earnings.*call', r'conference'],
    'presentation': [r'presentation', r'slide', r'prqtr'],
    'supplement': [r'supplement', r'additional', r'fsqtr'],
    'results': [r'results', r'financial', r'statement', r'rslt'],
    'data': [r'data', r'test_data', r'json', r'raw']
}

# Bank name inference from common banks
COMMON_BANKS = [
    'Citigroup', 'JPMorgan', 'BankOfAmerica', 'WellsFargo',
    'GoldmanSachs', 'MorganStanley', 'Barclays', 'HSBC'
]

def discover_and_process(
    raw_root: Path,
    parsers: Optional[Dict[str, Callable[[str, str, Path], Any]]] = None,
    skip_unsupported: bool = True,
    default_bank: str = "UnknownBank"
) -> None:
    """
    Discover and process files in the raw data directory structure.
    
    Supports flexible directory structures:
    1. raw_root/bank_name/quarter_name/files
    2. raw_root/quarter_name/files
    
    Args:
        raw_root: Root directory containing data files
        parsers: Dictionary mapping file extensions to parser functions.
                If None, uses default parsers.
        skip_unsupported: If True, skip unsupported file types with a warning.
                        If False, raise ValueError for unsupported file types.
        default_bank: Default bank name to use if bank can't be inferred
    """
    if not raw_root.exists() or not raw_root.is_dir():
        raise ValueError(f"Raw data directory does not exist: {raw_root}")
    
    # Use default parsers if none provided
    if parsers is None:
        parsers = _get_default_parsers()
    
    logger.info(f"Starting file discovery in: {raw_root}")
    
    # Check first level directories to determine structure
    first_level_dirs = [d for d in sorted(raw_root.iterdir())
                       if d.is_dir() and not d.name.startswith('.')]
    
    # Process based on structure detected
    for directory in first_level_dirs:
        dir_name = directory.name
        
        # Check if directory is a bank directory or quarter directory
        if any(bank.lower() in dir_name.lower() for bank in COMMON_BANKS):
            # Structure: raw_root/bank/quarter/files
            bank_name = dir_name
            logger.info(f"Processing bank directory: {bank_name}")
            
            # Process each quarter directory in this bank directory
            for quarter_dir in sorted(directory.iterdir()):
                if not quarter_dir.is_dir() or quarter_dir.name.startswith('.'):
                    continue
                
                quarter = quarter_dir.name
                logger.info(f"Processing quarter: {quarter} for bank: {bank_name}")
                _process_directory(quarter_dir, bank_name, quarter, parsers, skip_unsupported)
        
        elif _is_quarter_directory(dir_name):
            # Structure: raw_root/quarter/files
            quarter = dir_name
            logger.info(f"Processing quarter directory: {quarter} with default bank: {default_bank}")
            _process_directory(directory, default_bank, quarter, parsers, skip_unsupported)
        
        else:
            # Unknown directory type, try to process anyway
            logger.warning(f"Unknown directory type: {dir_name}, will attempt to process as data directory")
            # Try to infer quarter from name if possible
            quarter = _infer_quarter(dir_name) or "UnknownQuarter"
            _process_directory(directory, default_bank, quarter, parsers, skip_unsupported)

def _process_directory(
    directory: Path,
    bank_name: str,
    quarter: str,
    parsers: Dict[str, Callable],
    skip_unsupported: bool
) -> None:
    """Process all files in a directory with the appropriate parsers."""
    for file_path in sorted(directory.iterdir()):
        if not file_path.is_file() or file_path.name.startswith('.'):
            continue
        
        file_ext = file_path.suffix.lower()
        
        # Try to determine document type from filename
        doc_type = _infer_document_type(file_path.name)
        
        # Get the appropriate parser for this file extension
        parser = parsers.get(file_ext)
        
        if parser:
            try:
                logger.info(f"Processing file: {file_path} as {doc_type}")
                parser(bank_name, quarter, file_path, doc_type)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}", exc_info=True)
        elif not skip_unsupported:
            raise ValueError(f"No parser available for file: {file_path}")
        else:
            logger.warning(f"Skipping unsupported file type: {file_path}")

def _is_quarter_directory(dirname: str) -> bool:
    """Check if directory name matches quarter pattern (e.g. Q1 2025, Q2_2024)."""
    quarter_pattern = r'^Q[1-4][ _-]?20\d{2}$'
    return bool(re.match(quarter_pattern, dirname, re.IGNORECASE))

def _infer_quarter(dirname: str) -> Optional[str]:
    """Try to infer quarter from directory name."""
    # Look for Q1-Q4 followed by a year
    quarter_match = re.search(r'Q([1-4])[ _-]?(20\d{2})', dirname, re.IGNORECASE)
    if quarter_match:
        q_num, year = quarter_match.groups()
        return f"Q{q_num}_{year}"
    
    # Look for 1Q-4Q followed by a year
    alt_quarter_match = re.search(r'([1-4])Q[ _-]?(20\d{2})', dirname, re.IGNORECASE)
    if alt_quarter_match:
        q_num, year = alt_quarter_match.groups()
        return f"Q{q_num}_{year}"
    
    return None

def _infer_document_type(filename: str) -> str:
    """
    Infer document type from filename.
    Returns one of: transcript, presentation, supplement, results, or other
    """
    filename_lower = filename.lower()
    
    for doc_type, patterns in DOCUMENT_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, filename_lower):
                return doc_type
    
    return "other"

def _get_default_parsers() -> Dict[str, Callable]:
    """Get default parsers, initializing them on first call."""
    # Import parsers here to avoid circular imports
    from .parsers.pdf_parser import parse_pdf
    from .parsers.excel_parser import parse_excel
    from .parsers.json_parser import parse_json
    
    parsers = DEFAULT_PARSERS.copy()
    
    # Set up default parsers if available
    if parse_pdf:
        parsers['.pdf'] = parse_pdf
        # Also use PDF parser for text files
        parsers['.txt'] = parse_pdf
    
    if parse_excel:
        parsers['.xlsx'] = parse_excel
        parsers['.xls'] = parse_excel
        
    if parse_json:
        parsers['.json'] = parse_json
    
    # Add other parsers as they become available
    
    return {ext: parser for ext, parser in parsers.items() if parser is not None}

def process_file(
    file_path: Path,
    bank: str,
    quarter: str,
    parsers: Optional[Dict[str, Callable]] = None,
    doc_type: str = "unknown"
) -> Any:
    """
    Process a single file using the appropriate parser.
    
    Args:
        file_path: Path to the file to process
        bank: Bank name
        quarter: Quarter identifier
        parsers: Optional dictionary of file extensions to parser functions.
                If None, uses default parsers.
        doc_type: Type of document (transcript, presentation, etc.)
                If None, will be inferred from filename.
    
    Returns:
        The result of the parser function, or None if no parser was found.
    """
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if parsers is None:
        parsers = _get_default_parsers()
    
    if doc_type == "unknown":
        doc_type = _infer_document_type(file_path.name)
    
    file_ext = file_path.suffix.lower()
    parser = parsers.get(file_ext)
    
    if parser:
        logger.info(f"Processing {file_path} as {doc_type} with {parser.__name__}")
        return parser(bank, quarter, file_path, doc_type)
    else:
        logger.warning(f"No parser available for file: {file_path}")
        return None

def discover_files(
    raw_root: Path,
    extensions: Optional[List[str]] = None
) -> List[Tuple[str, str, Path, str]]:
    """
    Discover all files matching specified extensions in the directory structure.
    Returns a list of tuples containing (bank_name, quarter, file_path, document_type).
    
    Args:
        raw_root: Root directory to search in
        extensions: List of file extensions to look for (without the dot).
                  If None, all files will be included.
    
    Returns:
        List of tuples with (bank_name, quarter, file_path, document_type)
    """
    if not raw_root.exists() or not raw_root.is_dir():
        raise ValueError(f"Directory does not exist: {raw_root}")
    
    results = []
    
    # Walk through directory structure
    for dirpath, dirnames, filenames in os.walk(raw_root):
        dir_path = Path(dirpath)
        
        # Skip hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        
        # Parse path components to extract bank and quarter info
        path_parts = dir_path.relative_to(raw_root).parts if dir_path != raw_root else []
        
        bank_name = "UnknownBank"
        quarter = "UnknownQuarter"
        
        # Try to identify bank and quarter from path
        for part in path_parts:
            if any(bank.lower() in part.lower() for bank in COMMON_BANKS):
                bank_name = part
            elif _is_quarter_directory(part):
                quarter = part
            elif inferred_q := _infer_quarter(part):
                quarter = inferred_q
        
        for filename in filenames:
            # Skip hidden files
            if filename.startswith('.'):
                continue
                
            file_path = dir_path / filename
            
            # Check extension if specified
            if extensions and not any(file_path.name.lower().endswith(f".{ext.lower()}") for ext in extensions):
                continue
                
            doc_type = _infer_document_type(filename)
            results.append((bank_name, quarter, file_path, doc_type))
    
    return results
