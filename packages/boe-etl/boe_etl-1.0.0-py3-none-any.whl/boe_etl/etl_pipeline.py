import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Union

import pandas as pd
from .config import ConfigManager, ETLConfig, BankConfig
from .nlp_schema import NLPSchema
from .text_cleaning import TextCleaner
from .storage_config import get_storage_config
from .data_versioning import get_data_version_manager
from .version_tag_manager import get_version_tag_manager
from .topic_modeling import get_topic_modeler
from .metadata import MetadataManager
from .pdf_parser import get_pdf_parser
from .error_handling import get_exception_handler
from .progress_tracker import get_progress_tracker
from .schema_transformer import SchemaTransformer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ETLPipeline:
    """Complete ETL pipeline for processing bank earnings call data"""
    
    def __init__(self, config: Optional[ETLConfig] = None):
        """Initialize the ETL pipeline with configuration.
        
        Args:
            config: Optional ETLConfig instance. If not provided, will load default config.
        """
        # Initialize configuration
        self.config = config or ConfigManager().get_config()
        logger.info(f"Initializing ETL pipeline for {len(self.config.banks)} banks")
        
        # Initialize components
        self.storage = get_storage_config()
        self.version_manager = get_data_version_manager()
        self.tag_manager = get_version_tag_manager()
        self.topic_modeler = get_topic_modeler()
        self.metadata_manager = MetadataManager()
        self.text_cleaner = TextCleaner()
        
        # Set up data directories from config
        self.raw_data_dir = Path(self.config.processing.raw_data_dir)
        self.processed_data_dir = Path(self.config.processing.processed_data_dir)
        
        # Create directories if they don't exist
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Raw data directory: {self.raw_data_dir}")
        logger.info(f"Processed data directory: {self.processed_data_dir}")
        
        # Import file discovery here to avoid circular imports
        from .file_discovery import discover_files
        self.discover_files = discover_files
        
    def process_bank_data(
        self,
        bank_name: str,
        quarter: str,
        raw_data_path: Path
    ) -> None:
        """
        Process data for a specific bank and quarter
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
            raw_data_path: Path to raw data directory
        """
        try:
            logging.info(f"Starting ETL process for {bank_name} {quarter}")
            
            # 1. Load and parse raw data
            raw_data = self._load_raw_data(raw_data_path)
            
            # 2. Clean and normalize text
            cleaned_data = self._clean_text(raw_data)
            
            # 3. Apply topic modeling
            processed_data = self._apply_topic_modeling(cleaned_data, bank_name, quarter)
            
            # 4. Generate metadata
            metadata = self._generate_metadata(processed_data, bank_name, quarter)
            
            # 5. Store data with versioning
            version_id = self._store_data(processed_data, metadata, bank_name, quarter)
            
            # 6. Tag the version
            self._tag_version(version_id, bank_name, quarter)
            
            logging.info(f"ETL process completed successfully for {bank_name} {quarter}")
            
        except Exception as e:
            logging.error(f"ETL process failed for {bank_name} {quarter}: {e}")
            raise
    
    def _load_raw_data(self, raw_data_path: Path) -> List[Dict]:
        """Load raw data from various sources"""
        data = []
        for file in raw_data_path.glob("*.json"):
            with open(file, 'r') as f:
                record = json.load(f)
                record["source_file"] = file.name
                data.append(record)
        return data
    
    def _clean_text(self, raw_data: List[Dict]) -> List[Dict]:
        """Clean and normalize text data"""
        cleaned_data = []
        for record in raw_data:
            # Use the text_cleaner with its own configuration
            cleaned_text = self.text_cleaner.clean_text(record["text"])
            
            cleaned_record = {
                "text": cleaned_text,
                "original_text": record["text"],
                "speaker": record.get("speaker", "unknown"),
                "timestamp": record.get("timestamp", datetime.now().isoformat()),
                "source_file": record.get("source_file", "unknown")
            }
            cleaned_data.append(cleaned_record)
        return cleaned_data
    
    def _clean_text_records(self, nlp_records: List[Dict]) -> List[Dict]:
        """Clean text in NLP schema records"""
        cleaned_records = []
        for record in nlp_records:
            # Create a copy of the record
            cleaned_record = record.copy()
            
            # Clean the text field
            original_text = record.get("text", "")
            cleaned_text = self.text_cleaner.clean_text(original_text)
            
            # Update the record with cleaned text
            cleaned_record["text"] = cleaned_text
            cleaned_record["word_count"] = len(cleaned_text.split())
            cleaned_record["sentence_length"] = len(cleaned_text)
            
            # Only include records with meaningful text
            if cleaned_text.strip():
                cleaned_records.append(cleaned_record)
        
        return cleaned_records
    
    def _apply_topic_modeling(
        self,
        cleaned_data: List[Dict],
        bank_name: str,
        quarter: str
    ) -> List[Dict]:
        """Apply topic modeling to processed data"""
        processed_data = self.topic_modeler.process_batch(
            cleaned_data,
            bank_name=bank_name,
            quarter=quarter
        )
        return processed_data
    
    def _generate_metadata(
        self,
        processed_data: List[Dict],
        bank_name: str,
        quarter: str
    ) -> Dict:
        """Generate metadata for the processed data"""
        df = pd.DataFrame(processed_data)
        
        metadata = {
            "bank_name": bank_name,
            "quarter": quarter,
            "processing_date": datetime.now().isoformat(),
            "num_records": len(processed_data),
            "topic_distribution": df["topic_label"].value_counts().to_dict(),
            "speaker_distribution": (df["speaker_norm"] if "speaker_norm" in df.columns
                                   else df["speaker"] if "speaker" in df.columns
                                   else pd.Series()).value_counts().to_dict(),
            "processing_pipeline": "v1.0",
            "model_version": "BERTopic_v1.5",
            "cleaning_parameters": self.text_cleaner.get_parameters()
        }
        
        return metadata
    
    def _store_data(
        self,
        processed_data: List[Dict],
        metadata: Dict,
        bank_name: str,
        quarter: str
    ) -> str:
        """Store processed data with versioning"""
        # Create version
        version_info = {
            "processing_pipeline": metadata["processing_pipeline"],
            "model_version": metadata["model_version"],
            "cleaning_parameters": metadata["cleaning_parameters"],
            "num_records": metadata["num_records"]
        }
        
        version_id = self.version_manager.create_version(
            bank_name=bank_name,
            quarter=quarter,
            version_info=version_info
        )
        
        # Store processed data as Parquet
        df = pd.DataFrame(processed_data)
        version_path = self.version_manager._get_version_path(bank_name, quarter, version_id)
        parquet_path = version_path / "processed_data.parquet"
        df.to_parquet(parquet_path)
        
        # Store metadata
        metadata_path = version_path / "processing_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return version_id
    
    def _tag_version(self, version_id: str, bank_name: str, quarter: str) -> None:
        """Tag the processed version"""
        self.tag_manager.create_tag(
            tag_name="processed",
            bank_name=bank_name,
            quarter=quarter,
            version_id=version_id,
            description="Processed and topic-modeled version"
        )
    
    def process_all_banks(self) -> None:
        """Process all banks and quarters in the raw data directory.
        
        Uses flexible file discovery to process all files regardless of
        directory structure or naming convention.
        """
        logger.info("Starting flexible file discovery and processing")
        
        # Discover all files in the raw data directory
        try:
            files = self.discover_files(self.raw_data_dir)
            logger.info(f"Discovered {len(files)} files to process")
            
            if not files:
                logger.warning("No files found in the raw data directory")
                return
                
            # Process each file based on its type and location
            for bank_name, quarter, file_path, doc_type in files:
                try:
                    logger.info(f"Processing {doc_type} file: {file_path} for {bank_name} {quarter}")
                    self._process_discovered_file(bank_name, quarter, file_path, doc_type)
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
                    
        except Exception as e:
            logger.error(f"Error during file discovery: {e}", exc_info=True)
            
        # Also run the traditional config-based processing if banks are specified
        # This ensures backward compatibility with existing configurations
        if hasattr(self.config, 'banks') and self.config.banks:
            logger.info("Also processing banks from configuration")
            for bank in self.config.banks:
                try:
                    self._process_bank(bank)
                except Exception as e:
                    logger.error(f"Error processing bank {getattr(bank, 'name', 'unknown')}: {e}",
                                exc_info=True)
    
    def _process_bank(self, bank: BankConfig) -> None:
        """Process data for a single bank.
        
        Args:
            bank: Bank configuration object
        """
        bank_name = bank.name
        logger.info(f"Processing bank: {bank_name}")
        
        for quarter in bank.quarters:
            try:
                self._process_quarter(bank, quarter)
            except Exception as e:
                logger.error(f"Error processing {bank_name} {quarter}: {e}", 
                            exc_info=True)
    
    def _normalize_quarter(self, quarter: str) -> str:
        """Normalize quarter format to a standard form.
        
        Args:
            quarter: Quarter identifier in any format (e.g., 'Q1 2025', 'Q1_2025', 'Q1-2025')
            
        Returns:
            Normalized quarter string in standard format (e.g., 'Q1_2025')
        """
        # Extract quarter number and year using regex
        import re
        match = re.match(r'Q([1-4])[\s_-]*(\d{4})', quarter)
        if match:
            q_num, year = match.groups()
            return f"Q{q_num}_{year}"
        return quarter  # Return as is if no match
    
    def _find_quarter_directory(self, bank_name: str, quarter: str) -> Path:
        """Find the matching quarter directory regardless of format.
        
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier in normalized format
            
        Returns:
            Path to the quarter directory if found, or normalized path otherwise
        """
        # Try exact match first
        exact_path = self.raw_data_dir / bank_name / quarter
        if exact_path.exists():
            return exact_path
            
        # Extract quarter number and year for looser matching
        import re
        match = re.match(r'Q([1-4])_(\d{4})', quarter)
        if not match:
            return exact_path  # Return original if not in expected format
            
        q_num, year = match.groups()
        
        # Try common variations
        variations = [
            f"Q{q_num} {year}",
            f"Q{q_num}-{year}",
            f"Q{q_num}{year}",
            f"{q_num}Q{year}",
            f"{q_num}Q-{year}"
        ]
        
        for var in variations:
            var_path = self.raw_data_dir / bank_name / var
            if var_path.exists():
                logger.info(f"Found quarter directory with alternate format: {var_path}")
                return var_path
                
        return exact_path  # Return original if no alternatives found
    
    def _process_quarter(self, bank: BankConfig, quarter: str) -> None:
        """Process data for a specific quarter.
        
        Args:
            bank: Bank configuration object
            quarter: Quarter identifier (e.g., 'Q1_2025')
        """
        bank_name = bank.name
        normalized_quarter = self._normalize_quarter(quarter)
        logger.info(f"Processing {bank_name} - {quarter} (normalized: {normalized_quarter})")
        
        # Create quarter directory in processed data
        quarter_dir = self.processed_data_dir / bank_name / normalized_quarter
        quarter_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each data source
        for source in bank.data_sources:
            try:
                self._process_data_source(bank_name, quarter, source, quarter_dir)
            except Exception as e:
                logger.error(f"Error processing {source.type} for {bank_name} {quarter}: {e}", 
                            exc_info=True)
    
    def _process_data_source(self, bank_name: str, quarter: str, 
                           source: Any, output_dir: Path) -> None:
        """Process a single data source for a bank and quarter.
        
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
            source: Data source configuration
            output_dir: Directory to save processed data
        """
        source_type = getattr(source, 'type', 'unknown')
        logger.info(f"Processing {source_type} for {bank_name} {quarter}")
        
        # Extract the base name without extension
        file_pattern_base = Path(source.file_pattern).stem
        
        # Look for matching file with different extensions
        found_file = None
        candidates = []
        
        # First try the exact name from configuration
        source_file = self.raw_data_dir / bank_name / quarter / source.file_pattern
        if source_file.exists():
            found_file = source_file
        else:
            # Try to find matching files with alternative extensions
            possible_extensions = ['.pdf', '.txt', '.xlsx', '.csv', '.json']
            
            for ext in possible_extensions:
                candidate_file = self.raw_data_dir / bank_name / quarter / f"{file_pattern_base}{ext}"
                candidates.append(candidate_file)
                if candidate_file.exists():
                    found_file = candidate_file
                    logger.info(f"Found alternative file format: {candidate_file}")
                    break
        
        if not found_file:
            logger.warning(f"Source file not found: {source_file}")
            logger.debug(f"Tried alternatives: {candidates}")
            return
            
        # Process based on file extension
        file_ext = found_file.suffix.lower()
        if file_ext == '.pdf':
            self._process_pdf(found_file, output_dir, source_type)
        elif file_ext in ['.xlsx', '.xls']:
            self._process_excel(found_file, output_dir, source_type)
        elif file_ext == '.txt':
            # Text files can be processed by our enhanced PDF parser
            self._process_pdf(found_file, output_dir, source_type)
        else:
            logger.warning(f"Unsupported file format: {file_ext}")
    
    def _process_pdf(self, file_path: Path, output_dir: Path, source_type: str) -> None:
        """Process a PDF file.
        
        Args:
            file_path: Path to the PDF file
            output_dir: Directory to save processed data
            source_type: Type of the source (e.g., 'presentation', 'transcript')
        """
        logger.info(f"Processing PDF: {file_path}")
        
        try:
            # Use the PDF parser to extract text
            pdf_parser = get_pdf_parser()
            parsed_data = pdf_parser.parse_pdf(str(file_path), source_type)
            
            if not parsed_data:
                logger.warning(f"No data extracted from {file_path}")
                return
                
            logger.info(f"Extracted {len(parsed_data)} records from {file_path}")
            
            # Extract bank and quarter from directory structure
            bank_name = file_path.parts[-3]
            quarter = file_path.parts[-2]
            
            # Transform to NLP schema if parsed_data is in new format
            if isinstance(parsed_data, dict) and 'content' in parsed_data:
                # New parser format - use schema transformer
                schema_transformer = SchemaTransformer()
                nlp_records = schema_transformer.transform_parsed_data(parsed_data, bank_name, quarter)
                cleaned_data = self._clean_text_records(nlp_records)
            else:
                # Legacy format - use old cleaning method
                cleaned_data = self._clean_text(parsed_data)
            
            processed_data = self._apply_topic_modeling(cleaned_data, bank_name, quarter)
            metadata = self._generate_metadata(processed_data, bank_name, quarter)
            
            # Store data with version tracking
            version_id = self._store_data(processed_data, metadata, bank_name, quarter)
            self._tag_version(version_id, bank_name, quarter)
            
            logger.info(f"Successfully processed {file_path} - version: {version_id}")
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}", exc_info=True)
        
    def _process_excel(self, file_path: Path, output_dir: Path, source_type: str) -> None:
        """Process an Excel file.
        
        Args:
            file_path: Path to the Excel file
            output_dir: Directory to save processed data
            source_type: Type of the source
        """
        logger.info(f"Processing Excel: {file_path}")
        
        try:
            # Extract bank and quarter from directory structure
            bank_name = file_path.parts[-3]
            quarter = file_path.parts[-2]
            
            # Import and use the Excel parser
            from .parsers.excel_parser import ExcelParser
            
            # Parse the Excel file
            parser = ExcelParser(bank_name, quarter)
            parsed_data = parser.parse(file_path)
            
            if not parsed_data:
                logger.warning(f"No data extracted from {file_path}")
                return
                
            logger.info(f"Extracted data from {len(parsed_data.get('content', {}).get('tables', {}))} sheets from {file_path}")
            
            # Transform to NLP schema
            schema_transformer = SchemaTransformer()
            nlp_records = schema_transformer.transform_parsed_data(parsed_data, bank_name, quarter)
            
            if not nlp_records:
                logger.warning(f"No NLP records generated from {file_path}")
                return
            
            # Clean and process the data
            cleaned_data = self._clean_text_records(nlp_records)
            processed_data = self._apply_topic_modeling(cleaned_data, bank_name, quarter)
            metadata = self._generate_metadata(processed_data, bank_name, quarter)
            
            # Store data with version tracking
            version_id = self._store_data(processed_data, metadata, bank_name, quarter)
            self._tag_version(version_id, bank_name, quarter)
            
            logger.info(f"Successfully processed Excel file: {file_path} - version: {version_id}")
            
        except Exception as e:
            logger.error(f"Error processing Excel {file_path}: {e}", exc_info=True)
    
    def _process_discovered_file(self, bank_name: str, quarter: str, file_path: Path, doc_type: str) -> None:
        """Process a file discovered through flexible file discovery.
        
        Args:
            bank_name: Name of the bank (may be inferred)
            quarter: Quarter identifier (e.g., 'Q1_2025')
            file_path: Path to the file
            doc_type: Type of document (transcript, presentation, supplement, etc.)
        """
        logger.info(f"Processing discovered file: {file_path}")
        
        try:
            # Determine file type based on extension
            file_ext = file_path.suffix.lower()
            
            # Import the parser modules
            from .parsers import parse_file
            
            # Parse the file using the appropriate parser
            try:
                parsed_data = parse_file(bank_name, quarter, file_path, doc_type)
                
                if not parsed_data:
                    logger.warning(f"No data extracted from {file_path}")
                    return
            except ImportError as e:
                # If parser dependencies are missing, log and return
                logger.error(f"Parser dependencies missing: {e}")
                return
            except Exception as e:
                logger.error(f"Error parsing file {file_path}: {e}")
                return
            
            # Create output directory if needed
            output_dir = self.processed_data_dir / bank_name / quarter
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Transform to NLP schema using the schema transformer
            schema_transformer = SchemaTransformer()
            nlp_records = schema_transformer.transform_parsed_data(parsed_data, bank_name, quarter)
            
            if not nlp_records:
                logger.warning(f"No NLP records generated from {file_path}")
                return
            
            # Clean and process the data
            cleaned_data = self._clean_text_records(nlp_records)
            processed_data = self._apply_topic_modeling(cleaned_data, bank_name, quarter)
            metadata = self._generate_metadata(processed_data, bank_name, quarter)
            
            # Store data with version tracking
            version_id = self._store_data(processed_data, metadata, bank_name, quarter)
            self._tag_version(version_id, bank_name, quarter)
            
            logger.info(f"Successfully processed {doc_type} file: {file_path} - version: {version_id}")
        
        except Exception as e:
            logger.error(f"Error processing discovered file {file_path}: {e}", exc_info=True)
            

def run_etl_pipeline() -> None:
    """Run the ETL pipeline"""
    pipeline = ETLPipeline()
    pipeline.process_all_banks()

if __name__ == "__main__":
    run_etl_pipeline()
