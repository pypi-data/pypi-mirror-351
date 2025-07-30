import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json
import traceback
from .config import ConfigManager

class ETLExceptionHandler:
    """Centralized error handling and logging for ETL pipeline"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        
        # Try to determine what type of config we have
        if hasattr(self.config, "logging") and hasattr(self.config.logging, "file"):
            # If it's an object with logging.file attribute
            log_file = self.config.logging.file
        elif isinstance(self.config, dict) and "logging" in self.config and "file" in self.config["logging"]:
            # If it's a dictionary with config["logging"]["file"]
            log_file = self.config["logging"]["file"]
        else:
            # Default fallback
            log_file = "logs/etl.log"
        
        self.error_log_path = Path(log_file).parent / "error_logs"
        self.error_log_path.mkdir(parents=True, exist_ok=True)
        
    def handle_error(
        self,
        error: Exception,
        bank_name: str,
        quarter: str,
        stage: str,
        record: Optional[Dict] = None
    ) -> None:
        """
        Handle and log errors with detailed information
        Args:
            error: The exception that occurred
            bank_name: Name of the bank being processed
            quarter: Quarter identifier
            stage: Pipeline stage where error occurred
            record: The data record being processed (optional)
        """
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "bank_name": bank_name,
            "quarter": quarter,
            "stage": stage,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "record_info": record if record else "N/A"
        }
        
        # Log to file
        error_log_file = self.error_log_path / f"{bank_name}_{quarter}_errors.log"
        with open(error_log_file, 'a') as f:
            f.write(json.dumps(error_info, indent=2) + "\n")
        
        # Log to console
        logging.error(f"Error in {stage} for {bank_name} {quarter}: {error}")
        
    def get_error_summary(self, bank_name: str, quarter: str) -> Dict:
        """
        Get summary of errors for a specific bank and quarter
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
        Returns:
            Dictionary containing error summary
        """
        error_log_file = self.error_log_path / f"{bank_name}_{quarter}_errors.log"
        if not error_log_file.exists():
            return {"total_errors": 0, "error_types": {}}
            
        error_types = {}
        total_errors = 0
        
        with open(error_log_file, 'r') as f:
            for line in f:
                try:
                    error_info = json.loads(line)
                    error_type = error_info["error_type"]
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                    total_errors += 1
                except json.JSONDecodeError:
                    continue
        
        return {
            "total_errors": total_errors,
            "error_types": error_types,
            "bank_name": bank_name,
            "quarter": quarter
        }

class DataValidator:
    """Data validation for ETL pipeline"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.required_fields = {
            "transcript": ["text", "speaker", "timestamp"],
            "presentation": ["text", "page_number", "section"]
        }
        
    def validate_record(
        self,
        record: Dict,
        data_type: str,
        bank_name: str,
        quarter: str
    ) -> bool:
        """
        Validate a single record
        Args:
            record: The record to validate
            data_type: Type of data (transcript/presentation)
            bank_name: Name of the bank
            quarter: Quarter identifier
        Returns:
            True if valid, False otherwise
        """
        if data_type not in self.required_fields:
            raise ValueError(f"Unknown data type: {data_type}")
            
        missing_fields = []
        for field in self.required_fields[data_type]:
            if field not in record:
                missing_fields.append(field)
                
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            get_exception_handler().handle_error(
                ValueError(error_msg),
                bank_name,
                quarter,
                "validation",
                record
            )
            return False
            
        # Additional validations
        if not isinstance(record["text"], str) or not record["text"].strip():
            error_msg = "Text field is empty or not a string"
            get_exception_handler().handle_error(
                ValueError(error_msg),
                bank_name,
                quarter,
                "validation",
                record
            )
            return False
            
        return True
    
    def validate_batch(
        self,
        records: List[Dict],
        data_type: str,
        bank_name: str,
        quarter: str
    ) -> List[Dict]:
        """
        Validate a batch of records
        Args:
            records: List of records to validate
            data_type: Type of data
            bank_name: Name of the bank
            quarter: Quarter identifier
        Returns:
            List of valid records
        """
        valid_records = []
        for record in records:
            if self.validate_record(record, data_type, bank_name, quarter):
                valid_records.append(record)
        return valid_records

def get_exception_handler() -> ETLExceptionHandler:
    """Get the singleton exception handler instance"""
    if not hasattr(get_exception_handler, 'instance'):
        get_exception_handler.instance = ETLExceptionHandler()
    return get_exception_handler.instance

def get_data_validator() -> DataValidator:
    """Get the singleton data validator instance"""
    if not hasattr(get_data_validator, 'instance'):
        get_data_validator.instance = DataValidator()
    return get_data_validator.instance
