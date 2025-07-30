import pyarrow as pa
import pandas as pd
import logging
from pyarrow import parquet as pq
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Union, Type, Callable
from datetime import datetime
import os
from pathlib import Path
from .config import ConfigManager
from .utils import get_project_root

class NLPSchema:
    """Schema optimized for NLP processing"""
    
    @staticmethod
    def get_schema() -> pa.Schema:
        """Get the optimized NLP schema"""
        return pa.schema([
            # Core metadata
            pa.field("bank_name", pa.string(), nullable=False),
            pa.field("quarter", pa.string(), nullable=False),
            pa.field("call_id", pa.string(), nullable=False),
            
            # Source information
            pa.field("source_type", pa.string(), nullable=False),
            pa.field("file_path", pa.string(), nullable=False),
            
            # Timestamps
            pa.field("timestamp_epoch", pa.int64(), nullable=True),
            pa.field("timestamp_iso", pa.string(), nullable=True),
            
            # Speaker information
            pa.field("speaker_norm", pa.string(), nullable=False),
            pa.field("analyst_utterance", pa.bool_(), nullable=False),
            
            # Sentence-level information
            pa.field("sentence_id", pa.int32(), nullable=False),
            pa.field("text", pa.string(), nullable=False),
            
            # NLP-specific fields
            pa.field("sentence_length", pa.int32(), nullable=True),
            pa.field("word_count", pa.int32(), nullable=True),
            pa.field("sentiment_score", pa.float32(), nullable=True),
            pa.field("sentiment_label", pa.string(), nullable=True),
            pa.field("key_phrases", pa.list_(pa.string()), nullable=True),
            pa.field("named_entities", pa.list_(pa.string()), nullable=True),
            
            # Topic modeling
            pa.field("topic_labels", pa.list_(pa.string()), nullable=True),
            pa.field("topic_scores", pa.list_(pa.float32()), nullable=True),
            
            # Metadata
            pa.field("processing_date", pa.timestamp('s'), nullable=False),
            pa.field("processing_version", pa.string(), nullable=False)
        ])
    
    @staticmethod
    def get_partitioning_columns() -> List[str]:
        """Get columns for Parquet partitioning"""
        return ["bank_name", "quarter"]
    
    @staticmethod
    def get_processing_metadata() -> Dict[str, str]:
        """Get processing metadata"""
        return {
            "processing_date": datetime.now().isoformat(),
            "processing_version": "1.0.0"
        }

class NLPDataWriter:
    """Writer class for NLP-optimized data"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.schema = NLPSchema.get_schema()
        self.partition_cols = NLPSchema.get_partitioning_columns()
        
    def _get_output_path(self, bank_name: str, quarter: str) -> Path:
        """Get the output path for a given bank and quarter"""
        base_dir = get_project_root() / "data" / "clean"
        return base_dir / f"bank_name={bank_name}" / f"quarter={quarter}"
    
    def write_batch(
        self,
        data: List[Dict[str, Any]],
        bank_name: str,
        quarter: str
    ) -> None:
        """Write a batch of data to Parquet"""
        try:
            # Get output path
            output_dir = self._get_output_path(bank_name, quarter)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert to Arrow table
            df = pd.DataFrame(data)
            table = pa.Table.from_pandas(df, schema=self.schema)
            
            # Write to Parquet with partitioning
            pq.write_to_dataset(
                table,
                root_path=str(output_dir),
                partition_cols=self.partition_cols,
                compression='snappy',
                use_dictionary=True
            )
            
            logging.info(f"Wrote {len(data)} records to {output_dir}")
            
        except Exception as e:
            logging.error(f"Failed to write batch: {e}")
            raise
    
    def write_single(
        self,
        record: Dict[str, Any],
        bank_name: str,
        quarter: str
    ) -> None:
        """Write a single record to Parquet"""
        self.write_batch([record], bank_name, quarter)

class NLPDataReader:
    """Reader class for NLP-optimized data"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.schema = NLPSchema.get_schema()
        
    def read_bank_quarter(
        self,
        bank_name: str,
        quarter: str
    ) -> pd.DataFrame:
        """Read data for a specific bank and quarter"""
        try:
            # Get input path
            input_dir = self._get_input_path(bank_name, quarter)
            
            # Read Parquet dataset
            dataset = pq.ParquetDataset(
                str(input_dir),
                schema=self.schema,
                validate_schema=True
            )
            
            # Convert to DataFrame
            table = dataset.read()
            return table.to_pandas()
            
        except Exception as e:
            logging.error(f"Failed to read data: {e}")
            raise
    
    def read_all(
        self,
        bank_name: Optional[str] = None,
        quarter: Optional[str] = None
    ) -> pd.DataFrame:
        """Read data with optional filtering"""
        try:
            # Get base directory
            base_dir = get_project_root() / "data" / "clean"
            
            # Get all matching paths
            paths = []
            for bank_dir in base_dir.glob("bank_name=*"):
                if bank_name and bank_dir.name != f"bank_name={bank_name}":
                    continue
                    
                for quarter_dir in bank_dir.glob("quarter=*"):
                    if quarter and quarter_dir.name != f"quarter={quarter}":
                        continue
                        
                    paths.extend(list(quarter_dir.glob("*.parquet")))
            
            if not paths:
                raise ValueError("No matching data found")
                
            # Read and concatenate all matching files
            tables = []
            for path in paths:
                table = pq.read_table(str(path), schema=self.schema)
                tables.append(table)
            
            return pa.concat_tables(tables).to_pandas()
            
        except Exception as e:
            logging.error(f"Failed to read data: {e}")
            raise

def get_nlp_writer() -> NLPDataWriter:
    """Get the singleton NLP writer instance"""
    if not hasattr(get_nlp_writer, 'instance'):
        get_nlp_writer.instance = NLPDataWriter()
    return get_nlp_writer.instance

def get_nlp_reader() -> NLPDataReader:
    """Get the singleton NLP reader instance"""
    if not hasattr(get_nlp_reader, 'instance'):
        get_nlp_reader.instance = NLPDataReader()
    return get_nlp_reader.instance
