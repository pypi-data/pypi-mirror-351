from typing import List, Dict, Optional, Any
import pyarrow as pa
from pyarrow import parquet as pq
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from .config import ConfigManager

class SchemaError(Exception):
    """Base exception for schema-related errors"""
    pass

class SchemaVersion(Enum):
    """Schema version enum"""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V1_2 = "1.2"

class SchemaField:
    """Base class for schema fields"""
    def __init__(self, name: str, type: pa.DataType, required: bool = True):
        self.name = name
        self.type = type
        self.required = required

class Schema:
    """Base schema class"""
    def __init__(self, name: str, version: SchemaVersion, fields: List[SchemaField]):
        self.name = name
        self.version = version
        self.fields = fields
        
    def to_arrow_schema(self) -> pa.Schema:
        """Convert to PyArrow schema"""
        return pa.schema([
            pa.field(f.name, f.type, not f.required)
            for f in self.fields
        ])

class TranscriptSchema(Schema):
    """Schema for transcript data"""
    def __init__(self):
        fields = [
            SchemaField("bank", pa.string(), True),
            SchemaField("quarter", pa.string(), True),
            SchemaField("call_id", pa.string(), True),
            SchemaField("speaker", pa.string(), True),
            SchemaField("timestamp", pa.timestamp('s'), True),
            SchemaField("text", pa.string(), True),
            SchemaField("sentence_id", pa.string(), True),
            SchemaField("source_type", pa.string(), True),
            SchemaField("source_url", pa.string(), False),
            SchemaField("cleaned_text", pa.string(), False),
            SchemaField("sentiment_score", pa.float32(), False),
            SchemaField("topic_labels", pa.list_(pa.string()), False),
            SchemaField("metadata", pa.string(), False)  # JSON string
        ]
        super().__init__("transcript", SchemaVersion.V1_2, fields)

class PresentationSchema(Schema):
    """Schema for presentation data"""
    def __init__(self):
        fields = [
            SchemaField("bank", pa.string(), True),
            SchemaField("quarter", pa.string(), True),
            SchemaField("presentation_id", pa.string(), True),
            SchemaField("slide_number", pa.int32(), True),
            SchemaField("title", pa.string(), True),
            SchemaField("content", pa.string(), True),
            SchemaField("timestamp", pa.timestamp('s'), True),
            SchemaField("source_type", pa.string(), True),
            SchemaField("source_url", pa.string(), False),
            SchemaField("metadata", pa.string(), False)
        ]
        super().__init__("presentation", SchemaVersion.V1_1, fields)

class StorageManager:
    """Manager for data storage operations"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config().data_storage
        self.schemas = {
            "transcript": TranscriptSchema(),
            "presentation": PresentationSchema()
        }
        
    def get_schema(self, name: str) -> Schema:
        """Get schema by name"""
        if name not in self.schemas:
            raise SchemaError(f"Schema '{name}' not found")
        return self.schemas[name]
    
    def write_parquet(
        self, 
        data: List[Dict[str, Any]], 
        schema_name: str, 
        output_path: Path
    ) -> None:
        """Write data to Parquet file with schema validation"""
        try:
            # Get schema
            schema = self.get_schema(schema_name)
            arrow_schema = schema.to_arrow_schema()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Validate data against schema
            self._validate_data(df, arrow_schema)
            
            # Write to Parquet
            table = pa.Table.from_pandas(df, schema=arrow_schema)
            pq.write_table(
                table,
                output_path,
                compression=self.config.parquet_options.get('compression', 'snappy'),
                use_dictionary=True
            )
            
        except Exception as e:
            raise SchemaError(f"Failed to write Parquet: {e}")
    
    def _validate_data(self, df: pd.DataFrame, schema: pa.Schema) -> None:
        """Validate DataFrame against schema"""
        for field in schema:
            if field.required and df[field.name].isnull().any():
                raise SchemaError(f"Missing required field: {field.name}")
            
            # Type validation
            if field.type == pa.string():
                if df[field.name].dtype != 'O':
                    raise SchemaError(f"Field {field.name} should be string")
            elif field.type == pa.timestamp('s'):
                if not pd.api.types.is_datetime64_any_dtype(df[field.name]):
                    raise SchemaError(f"Field {field.name} should be datetime")
    
    def read_parquet(self, path: Path, schema_name: str) -> pd.DataFrame:
        """Read Parquet file with schema validation"""
        try:
            # Get schema
            schema = self.get_schema(schema_name)
            arrow_schema = schema.to_arrow_schema()
            
            # Read Parquet
            table = pq.read_table(path, schema=arrow_schema)
            df = table.to_pandas()
            
            # Validate data
            self._validate_data(df, arrow_schema)
            return df
            
        except Exception as e:
            raise SchemaError(f"Failed to read Parquet: {e}")
    
    def get_metadata(self, path: Path) -> Dict[str, Any]:
        """Get metadata from Parquet file"""
        try:
            metadata = pq.read_metadata(str(path))
            return json.loads(metadata.metadata.get(b'etl_metadata', b'{}'))
        except Exception as e:
            raise SchemaError(f"Failed to get metadata: {e}")
    
    def add_metadata(
        self, 
        path: Path, 
        metadata: Dict[str, Any]
    ) -> None:
        """Add metadata to Parquet file"""
        try:
            # Read existing metadata
            existing_metadata = self.get_metadata(path)
            
            # Merge with new metadata
            merged_metadata = {**existing_metadata, **metadata}
            
            # Write back with updated metadata
            table = pq.read_table(str(path))
            pq.write_table(
                table,
                str(path),
                metadata={
                    **table.schema.metadata,
                    b'etl_metadata': json.dumps(merged_metadata).encode('utf-8')
                }
            )
        except Exception as e:
            raise SchemaError(f"Failed to add metadata: {e}")

def get_storage_manager() -> StorageManager:
    """Get the singleton storage manager instance"""
    if not hasattr(get_storage_manager, 'instance'):
        get_storage_manager.instance = StorageManager()
    return get_storage_manager.instance
