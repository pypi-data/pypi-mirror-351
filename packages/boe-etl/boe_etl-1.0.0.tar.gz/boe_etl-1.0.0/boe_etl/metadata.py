from typing import Dict, List, Optional, Any, Union, Type, Callable
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum
from .config import ConfigManager

class MetadataType(Enum):
    """Types of metadata"""
    PROCESSING = "processing"
    QUALITY = "quality"
    PROVENANCE = "provenance"
    ANALYSIS = "analysis"

class MetadataError(Exception):
    """Base exception for metadata-related errors"""
    pass

@dataclass
class ProcessingMetadata:
    """Metadata about processing steps"""
    version: str
    processed_at: datetime
    pipeline_steps: List[str]
    parameters: Dict[str, Any]
    duration_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "processed_at": self.processed_at.isoformat(),
            "pipeline_steps": self.pipeline_steps,
            "parameters": self.parameters,
            "duration_seconds": self.duration_seconds
        }

@dataclass
class QualityMetadata:
    """Metadata about data quality"""
    text_length: int
    sentence_count: int
    word_count: int
    sentiment_score: Optional[float]
    topic_confidence: Optional[float]
    language_detected: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text_length": self.text_length,
            "sentence_count": self.sentence_count,
            "word_count": self.word_count,
            "sentiment_score": self.sentiment_score,
            "topic_confidence": self.topic_confidence,
            "language_detected": self.language_detected
        }

@dataclass
class ProvenanceMetadata:
    """Metadata about data provenance"""
    source_url: str
    source_type: str
    extraction_date: datetime
    extraction_tool: str
    file_size_bytes: int
    checksum: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_url": self.source_url,
            "source_type": self.source_type,
            "extraction_date": self.extraction_date.isoformat(),
            "extraction_tool": self.extraction_tool,
            "file_size_bytes": self.file_size_bytes,
            "checksum": self.checksum
        }

@dataclass
class AnalysisMetadata:
    """Metadata about analysis results"""
    topics: List[str]
    sentiment_trend: str
    speaker_sentiment: Dict[str, float]
    key_phrases: List[str]
    confidence_scores: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "topics": self.topics,
            "sentiment_trend": self.sentiment_trend,
            "speaker_sentiment": self.speaker_sentiment,
            "key_phrases": self.key_phrases,
            "confidence_scores": self.confidence_scores
        }

class MetadataManager:
    """Manager for metadata operations"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.metadata_types = {
            MetadataType.PROCESSING: ProcessingMetadata,
            MetadataType.QUALITY: QualityMetadata,
            MetadataType.PROVENANCE: ProvenanceMetadata,
            MetadataType.ANALYSIS: AnalysisMetadata
        }
    
    def create_metadata(
        self,
        metadata_type: MetadataType,
        **kwargs
    ) -> Dict[str, Any]:
        """Create metadata of specified type"""
        try:
            metadata_class = self.metadata_types[metadata_type]
            metadata = metadata_class(**kwargs)
            return metadata.to_dict()
        except Exception as e:
            raise MetadataError(f"Failed to create metadata: {e}")
    
    def merge_metadata(
        self,
        existing: Dict[str, Any],
        new: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two metadata dictionaries"""
        try:
            merged = existing.copy()
            for key, value in new.items():
                if key in merged:
                    # Handle nested dictionaries
                    if isinstance(merged[key], dict) and isinstance(value, dict):
                        merged[key] = {**merged[key], **value}
                    else:
                        merged[key] = value
                else:
                    merged[key] = value
            return merged
        except Exception as e:
            raise MetadataError(f"Failed to merge metadata: {e}")
    
    def validate_metadata(
        self,
        metadata: Dict[str, Any],
        metadata_type: MetadataType
    ) -> None:
        """Validate metadata against type requirements"""
        try:
            required_fields = set(self.metadata_types[metadata_type].__annotations__.keys())
            present_fields = set(metadata.keys())
            
            missing_fields = required_fields - present_fields
            if missing_fields:
                raise MetadataError(f"Missing required fields: {missing_fields}")
                
            # Validate field types
            for field, field_type in self.metadata_types[metadata_type].__annotations__.items():
                if field in metadata:
                    value = metadata[field]
                    if not isinstance(value, field_type):
                        raise MetadataError(f"Field {field} has incorrect type")
        except Exception as e:
            raise MetadataError(f"Failed to validate metadata: {e}")
    
    def write_metadata(
        self,
        path: Path,
        metadata: Dict[str, Any],
        metadata_type: MetadataType
    ) -> None:
        """Write metadata to file"""
        try:
            # Create metadata directory if needed
            metadata_dir = path.parent / "metadata"
            metadata_dir.mkdir(parents=True, exist_ok=True)
            
            # Write metadata file
            metadata_path = metadata_dir / f"{path.stem}_{metadata_type.value}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=4)
                
        except Exception as e:
            raise MetadataError(f"Failed to write metadata: {e}")
    
    def read_metadata(
        self,
        path: Path,
        metadata_type: MetadataType
    ) -> Dict[str, Any]:
        """Read metadata from file"""
        try:
            metadata_path = path.parent / "metadata" / f"{path.stem}_{metadata_type.value}.json"
            if not metadata_path.exists():
                return {}
                
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                self.validate_metadata(metadata, metadata_type)
                return metadata
        except Exception as e:
            raise MetadataError(f"Failed to read metadata: {e}")

def get_metadata_manager() -> MetadataManager:
    """Get the singleton metadata manager instance"""
    if not hasattr(get_metadata_manager, 'instance'):
        get_metadata_manager.instance = MetadataManager()
    return get_metadata_manager.instance
