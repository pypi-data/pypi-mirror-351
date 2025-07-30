import os
from pathlib import Path
from typing import Dict, Optional, Any, Union, Type, Callable, List
from .config import ConfigManager
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

class StorageConfig:
    """Configuration for local storage paths"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.project_root = Path(__file__).parent.parent.parent
        self.storage_path = self.project_root / "data"
        
        # Create required directories
        self._create_directories()
    
    def _create_directories(self):
        """Create required storage directories"""
        required_dirs = [
            "raw",  # Raw data storage
            "processed",  # Processed data
            "models",  # Model checkpoints
            "visualizations",  # Visualization outputs
            "logs",  # Log files
            "temp",  # Temporary files
            "config",  # Configuration files
            "metadata"  # Metadata storage
        ]
        
        for dir_name in required_dirs:
            dir_path = self.storage_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory: {dir_path}")
    
    @property
    def raw_data_path(self) -> Path:
        """Path for raw data storage"""
        return self.storage_path / "raw"
    
    @property
    def processed_data_path(self) -> Path:
        """Path for processed data storage"""
        return self.storage_path / "processed"
    
    @property
    def models_path(self) -> Path:
        """Path for model checkpoints"""
        return self.storage_path / "models"
    
    @property
    def visualizations_path(self) -> Path:
        """Path for visualization outputs"""
        return self.storage_path / "visualizations"
    
    @property
    def logs_path(self) -> Path:
        """Path for log files"""
        return self.storage_path / "logs"
    
    @property
    def temp_path(self) -> Path:
        """Path for temporary files"""
        return self.storage_path / "temp"
    
    @property
    def config_path(self) -> Path:
        """Path for configuration files"""
        return self.storage_path / "config"
    
    @property
    def metadata_path(self) -> Path:
        """Path for metadata storage"""
        return self.storage_path / "metadata"
    
    @property
    def parquet_path(self) -> Path:
        """Path for Parquet files"""
        return self.processed_data_path / "parquet"
    
    def get_bank_data_path(self, bank_name: str, quarter: str) -> Path:
        """Get path for bank-specific data"""
        return self.parquet_path / bank_name / quarter
    
    def get_topic_model_path(self, model_name: str) -> Path:
        """Get path for topic model checkpoints"""
        return self.models_path / "topic_models" / model_name
    
    def get_visualization_path(self, bank_name: str, quarter: str) -> Path:
        """Get path for visualization outputs"""
        return self.visualizations_path / bank_name / quarter
    
    def get_log_file_path(self, log_name: str) -> Path:
        """Get path for log files"""
        return self.logs_path / f"{log_name}.log"
    
    def get_metadata_path(self, bank_name: str, quarter: str) -> Path:
        """Get path for metadata files"""
        return self.metadata_path / bank_name / quarter

def get_storage_config() -> StorageConfig:
    """Get the singleton storage config instance"""
    if not hasattr(get_storage_config, 'instance'):
        get_storage_config.instance = StorageConfig()
    return get_storage_config.instance
