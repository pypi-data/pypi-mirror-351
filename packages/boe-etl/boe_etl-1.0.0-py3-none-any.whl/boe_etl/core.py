#!/usr/bin/env python3
"""
BoE ETL Core Module
===================

Core functionality for the BoE ETL package.
Provides the main ETLPipeline class and high-level processing functions.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import logging

from .etl_pipeline import ETLPipeline as _ETLPipeline
from .schema_transformer import SchemaTransformer
from .config import Config
from .parsers import PDFParser, ExcelParser, TextParser, JSONParser


class ETLPipeline:
    """
    Main ETL Pipeline class for processing financial documents.
    
    This class provides a high-level interface for processing various document types
    and converting them to standardized NLP-ready formats.
    
    Example:
        >>> pipeline = ETLPipeline()
        >>> results = pipeline.process_document('earnings_call.pdf', 'JPMorgan', 'Q1_2025')
        >>> df = pipeline.to_dataframe(results)
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the ETL pipeline.
        
        Args:
            config: Optional configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self.pipeline = _ETLPipeline(config=self.config)
        self.transformer = SchemaTransformer()
        self.logger = logging.getLogger(__name__)
        
        # Initialize parsers
        self.parsers = {
            '.pdf': PDFParser,
            '.txt': TextParser,
            '.xlsx': ExcelParser,
            '.xls': ExcelParser,
            '.csv': ExcelParser,
            '.json': JSONParser,
        }
    
    def process_document(self, 
                        file_path: Union[str, Path], 
                        institution: str, 
                        quarter: str,
                        include_nlp: bool = True) -> List[Dict[str, Any]]:
        """
        Process a single document through the ETL pipeline.
        
        Args:
            file_path: Path to the document to process
            institution: Name of the financial institution
            quarter: Quarter identifier (e.g., 'Q1_2025')
            include_nlp: Whether to include NLP features in the output
            
        Returns:
            List of processed records as dictionaries
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file type is not supported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check if file type is supported
        file_ext = file_path.suffix.lower()
        if file_ext not in self.parsers:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        self.logger.info(f"Processing {file_path} for {institution} {quarter}")
        
        try:
            # Process through the main pipeline
            results = self.pipeline.process_file(file_path, institution, quarter)
            
            if include_nlp and results:
                # Add NLP features
                df = pd.DataFrame(results)
                enhanced_df = self.transformer.add_nlp_features(df)
                results = enhanced_df.to_dict('records')
            
            self.logger.info(f"Successfully processed {len(results)} records")
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
            raise
    
    def process_directory(self, 
                         directory_path: Union[str, Path], 
                         institution: str, 
                         quarter: str,
                         include_nlp: bool = True,
                         recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Process all supported documents in a directory.
        
        Args:
            directory_path: Path to the directory containing documents
            institution: Name of the financial institution
            quarter: Quarter identifier (e.g., 'Q1_2025')
            include_nlp: Whether to include NLP features in the output
            recursive: Whether to search subdirectories
            
        Returns:
            List of processed records from all documents
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find all supported files
        pattern = "**/*" if recursive else "*"
        all_files = list(directory_path.glob(pattern))
        
        supported_files = [
            f for f in all_files 
            if f.is_file() and f.suffix.lower() in self.parsers
        ]
        
        if not supported_files:
            self.logger.warning(f"No supported files found in {directory_path}")
            return []
        
        self.logger.info(f"Processing {len(supported_files)} files from {directory_path}")
        
        all_results = []
        for file_path in supported_files:
            try:
                results = self.process_document(file_path, institution, quarter, include_nlp)
                all_results.extend(results)
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {str(e)}")
                continue
        
        return all_results
    
    def to_dataframe(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert processing results to a pandas DataFrame.
        
        Args:
            results: List of processed records
            
        Returns:
            pandas DataFrame with the processed data
        """
        if not results:
            return pd.DataFrame()
        
        return pd.DataFrame(results)
    
    def save_results(self, 
                    results: List[Dict[str, Any]], 
                    output_path: Union[str, Path],
                    format: str = 'csv') -> None:
        """
        Save processing results to a file.
        
        Args:
            results: List of processed records
            output_path: Path where to save the results
            format: Output format ('csv', 'parquet', 'json')
        """
        if not results:
            self.logger.warning("No results to save")
            return
        
        output_path = Path(output_path)
        df = self.to_dataframe(results)
        
        if format.lower() == 'csv':
            df.to_csv(output_path, index=False)
        elif format.lower() == 'parquet':
            df.to_parquet(output_path, index=False)
        elif format.lower() == 'json':
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Results saved to {output_path}")
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported file extensions
        """
        return list(self.parsers.keys())
    
    def validate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate processing results against the expected schema.
        
        Args:
            results: List of processed records
            
        Returns:
            Validation report dictionary
        """
        if not results:
            return {
                'valid': False,
                'errors': ['No results to validate'],
                'record_count': 0,
                'column_count': 0
            }
        
        df = self.to_dataframe(results)
        
        # Basic validation
        required_columns = ['text', 'speaker_norm', 'institution', 'quarter', 'source_file']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        errors = []
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check for empty text
        if 'text' in df.columns:
            empty_text_count = df['text'].isna().sum() + (df['text'] == '').sum()
            if empty_text_count > 0:
                errors.append(f"Found {empty_text_count} records with empty text")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'record_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns)
        }


# Convenience functions for quick processing
def process_file(file_path: Union[str, Path], 
                institution: str, 
                quarter: str,
                include_nlp: bool = True) -> pd.DataFrame:
    """
    Quick function to process a single file and return a DataFrame.
    
    Args:
        file_path: Path to the file to process
        institution: Institution name
        quarter: Quarter identifier
        include_nlp: Whether to include NLP features
        
    Returns:
        DataFrame with processed results
    """
    pipeline = ETLPipeline()
    results = pipeline.process_document(file_path, institution, quarter, include_nlp)
    return pipeline.to_dataframe(results)


def process_directory(directory_path: Union[str, Path], 
                     institution: str, 
                     quarter: str,
                     include_nlp: bool = True) -> pd.DataFrame:
    """
    Quick function to process all files in a directory and return a DataFrame.
    
    Args:
        directory_path: Path to the directory
        institution: Institution name
        quarter: Quarter identifier
        include_nlp: Whether to include NLP features
        
    Returns:
        DataFrame with processed results from all files
    """
    pipeline = ETLPipeline()
    results = pipeline.process_directory(directory_path, institution, quarter, include_nlp)
    return pipeline.to_dataframe(results)