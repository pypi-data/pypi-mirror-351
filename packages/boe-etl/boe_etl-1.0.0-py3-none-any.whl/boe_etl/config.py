import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator, ValidationError

# Set up logging
LOGGER = logging.getLogger(__name__)

class ConfigError(Exception):
    """Base exception for configuration errors"""
    pass

class DataSourceConfig(BaseModel):
    """Configuration for a data source"""
    type: str
    format: str
    file_pattern: str

class BankConfig(BaseModel):
    """Configuration for a bank"""
    name: str
    quarters: List[str]
    data_sources: List[DataSourceConfig]

class TextCleaningConfig(BaseModel):
    """Configuration for text cleaning operations"""
    # Text cleaning options
    remove_stopwords: bool = False  # Changed default to False to preserve context
    min_word_length: int = 2  # Reduced to capture important short terms (e.g., 'AI', 'IT')
    max_word_length: int = 50
    
    # Character-level cleaning
    remove_punctuation: bool = False  # Changed default to preserve financial terms
    remove_special_chars: bool = False  # Changed default to preserve financial symbols
    preserve_special_chars: List[str] = Field(
        default_factory=lambda: ['%', '$', '£', '€', '#', '@', '&', '/', '-', '_', '+', '=']
    )
    
    # Number handling
    remove_numbers: bool = False  # Changed default to preserve numerical context
    preserve_numbers_with_units: bool = True  # New: Preserve numbers with units (e.g., '10%', '2x')
    
    # Advanced processing
    lemmatize: bool = True
    use_financial_terms: bool = False  # Disabled by default to prevent attribute errors
    
    # Fillers and replacements
    replace_fillers: Dict[str, str] = Field(
        default_factory=lambda: {
            '&': 'and',
            'vs.': 'versus',
            'e.g.': 'for example',
            'i.e.': 'that is',
            'etc.': 'and so on'
        }
    )
    
    # Custom stopwords to remove (in addition to standard ones if remove_stopwords=True)
    custom_stopwords: List[str] = Field(
        default_factory=lambda: [
            's', 't', 'm', 're', 've', 'll', 'd', 'don', 'don\'t', 'doesn', 'doesn\'t',
            'isn', 'isn\'t', 'aren', 'aren\'t', 'wasn', 'wasn\'t', 'weren', 'weren\'t',
            'haven', 'haven\'t', 'hasn', 'hasn\'t', 'hadn', 'hadn\'t', 'won', 'won\'t',
            'wouldn', 'wouldn\'t', 'shan', 'shan\'t', 'shouldn', 'shouldn\'t', 'mightn',
            'mightn\'t', 'mustn', 'mustn\'t', 'couldn', 'couldn\'t', 'needn', 'needn\'t',
            'would', 'could', 'should', 'might', 'must', 'need', 'may', 'can', 'shall',
            'also', 'even', 'just', 'like', 'one', 'two', 'three', 'four', 'five', 'six',
            'seven', 'eight', 'nine', 'ten', 'first', 'second', 'third', 'fourth', 'fifth',
            'sixth', 'seventh', 'eighth', 'ninth', 'tenth'
        ]
    )

class TopicModelingConfig(BaseModel):
    """Configuration for topic modeling"""
    num_topics: int = 10
    min_topic_size: int = 5
    n_gram_range: List[int] = [1, 2]
    embedding_model: str = "all-MiniLM-L6-v2"

class SentimentAnalysisConfig(BaseModel):
    """Configuration for sentiment analysis"""
    model_name: str = "ProsusAI/finbert"
    batch_size: int = 32

class ProcessingConfig(BaseModel):
    """Processing configuration"""
    # Directory settings
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    log_dir: str = "logs"
    
    # NLP configurations
    text_cleaning: TextCleaningConfig = Field(default_factory=TextCleaningConfig)
    topic_modeling: TopicModelingConfig = Field(default_factory=TopicModelingConfig)
    sentiment_analysis: SentimentAnalysisConfig = Field(default_factory=SentimentAnalysisConfig)

class ConfigError(Exception):
    """Base exception for configuration errors"""
    pass

class TextCleaningConfig(BaseModel):
    """Configuration for text cleaning operations"""
    remove_stopwords: bool = True
    min_word_length: int = 3
    max_word_length: int = 50
    remove_numbers: bool = True
    remove_punctuation: bool = True
    remove_special_chars: bool = True
    replace_fillers: Dict[str, str] = Field(default_factory=dict)
    
    @validator('min_word_length')
    def validate_min_word_length(cls, v):
        if v < 1:
            raise ValueError('min_word_length must be at least 1')
        return v
    
    @validator('max_word_length')
    def validate_max_word_length(cls, v, values):
        if v < values.get('min_word_length', 1):
            raise ValueError('max_word_length must be greater than min_word_length')
        return v

class SpeakerNormalizationConfig(BaseModel):
    """Configuration for speaker name normalization"""
    title_case: bool = True
    remove_honorifics: bool = True
    honorifics: List[str] = Field(default_factory=lambda: ['mr', 'mrs', 'ms', 'dr', 'prof'])
    standardize_role_titles: bool = True
    role_title_map: Dict[str, str] = Field(default_factory=dict)

class TimestampConfig(BaseModel):
    """Configuration for timestamp handling"""
    timezone: str = 'UTC'
    date_format: str = '%Y-%m-%dT%H:%M:%S'
    fallback_date: str = Field(default_factory=lambda: datetime.now().isoformat())

class DataStorageConfig(BaseModel):
    """Configuration for data storage paths and formats"""
    raw_data_dir: Path = Path('data/raw')
    processed_data_dir: Path = Path('data/processed')
    db_path: Path = Path('db/earnings.db')
    log_path: Path = Path('logs/etl.log')
    parquet_options: Dict[str, str] = Field(default_factory=lambda: {
        'engine': 'pyarrow',
        'compression': 'snappy'
    })

class ETLConfig(BaseModel):
    """Main ETL configuration class"""
    # Bank configuration
    banks: List[BankConfig]
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    
    # Text cleaning settings
    text_cleaning: TextCleaningConfig = Field(default_factory=TextCleaningConfig)
    speaker_normalization: SpeakerNormalizationConfig = Field(default_factory=SpeakerNormalizationConfig)
    timestamp: TimestampConfig = Field(default_factory=TimestampConfig)
    data_storage: DataStorageConfig = Field(default_factory=DataStorageConfig)
    
    # Process settings
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    batch_size: int = 1000
    
    @validator('banks', pre=True)
    def validate_banks(cls, v):
        if not isinstance(v, list):
            raise ValueError("'banks' must be a list")
        if not v:
            raise ValueError("At least one bank must be configured")
        return v
    
    @validator('data_storage')
    def validate_paths(cls, v):
        for path in [v.raw_data_dir, v.processed_data_dir, v.db_path, v.log_path]:
            if not isinstance(path, Path):
                raise ValueError(f'Path {path} must be a pathlib.Path object')
        return v

class ConfigManager:
    """Configuration manager for ETL pipeline"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager"""
        self.config_path = config_path or Path('config/etl_config.yaml')
        self._config = None
        self.load_config()
    
    def _load_yaml_config(self) -> dict:
        """Load configuration from YAML file"""
        LOGGER.info(f"Loading configuration from {self.config_path}")
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config_dict = yaml.safe_load(f) or {}
        
        LOGGER.debug(f"Raw YAML content: {config_dict!r}")
        return config_dict
    
    def _apply_environment_overrides(self, config_dict: dict) -> dict:
        """Apply environment variable overrides to config"""
        for key, value in os.environ.items():
            if not key.startswith('ETL_'):
                continue
                
            # Convert ETL_BANKS_0_NAME to ['banks', '0', 'name']
            parts = key[4:].lower().split('__')
            current = config_dict
            
            try:
                for part in parts[:-1]:
                    # Handle list indices (e.g., '0' in 'banks.0.name')
                    if part.isdigit() and isinstance(current, list):
                        part = int(part)
                        if part >= len(current):
                            current.append({})
                    elif part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Convert string values to appropriate types
                if isinstance(value, str):
                    if value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    elif value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
                        value = float(value)
                
                current[parts[-1]] = value
                LOGGER.debug(f"Applied environment override: {key} = {value}")
                
            except (KeyError, IndexError, AttributeError) as e:
                LOGGER.warning(f"Failed to apply environment override {key}: {e}")
        
        return config_dict
    
    def load_config(self) -> None:
        """Load and validate configuration"""
        try:
            # Load environment variables
            load_dotenv()
            
            # Load and parse YAML config
            config_dict = self._load_yaml_config()
            
            # Apply environment variable overrides
            config_dict = self._apply_environment_overrides(config_dict)
            
            # Validate and create config object
            self._config = ETLConfig(**config_dict)
            LOGGER.info(f"Successfully loaded configuration with {len(self._config.banks)} banks")
            
        except Exception as e:
            LOGGER.error(f"Failed to load configuration: {e}", exc_info=True)
            raise ConfigError(f"Configuration error: {e}") from e
    
    def get_config(self) -> ETLConfig:
        """Get the validated configuration"""
        if self._config is None:
            raise ConfigError("Configuration not loaded")
        return self._config

def get_config_manager() -> ConfigManager:
    """Get the singleton config manager instance"""
    if not hasattr(get_config_manager, 'instance'):
        get_config_manager.instance = ConfigManager()
    return get_config_manager.instance
