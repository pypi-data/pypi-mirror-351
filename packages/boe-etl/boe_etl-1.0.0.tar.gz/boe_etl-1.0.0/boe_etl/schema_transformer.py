"""
Schema transformation module for converting parser outputs to NLP schema format.

This module handles the transformation of parsed data from various file types
(PDF, Excel, JSON, Text) into the standardized NLP schema format defined in nlp_schema.py.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

import pandas as pd
import pyarrow as pa
from nltk.tokenize import sent_tokenize

from .nlp_schema import NLPSchema
from .config import ConfigManager

logger = logging.getLogger(__name__)


class SchemaTransformer:
    """Transforms parsed data into NLP schema format."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the schema transformer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or ConfigManager().get_config()
        self.schema = NLPSchema.get_schema()
        
        # Initialize NLTK for sentence tokenization
        try:
            import nltk
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            import nltk
            nltk.download('punkt')
    
    def transform_parsed_data(
        self, 
        parsed_data: Dict[str, Any], 
        bank_name: str, 
        quarter: str
    ) -> List[Dict[str, Any]]:
        """Transform parsed data to NLP schema format.
        
        Args:
            parsed_data: Output from any parser (PDF, Excel, JSON, etc.)
            bank_name: Name of the bank
            quarter: Quarter identifier
            
        Returns:
            List of records conforming to NLP schema
        """
        try:
            # Determine the source type and transform accordingly
            document_type = parsed_data.get('document_type', 'unknown')
            file_path = parsed_data.get('file_path', '')
            
            if 'content' in parsed_data:
                if isinstance(parsed_data['content'], str):
                    # Simple text content (PDF, text files)
                    return self._transform_text_content(
                        parsed_data, bank_name, quarter
                    )
                elif isinstance(parsed_data['content'], dict):
                    if 'tables' in parsed_data['content']:
                        # Excel content with tables
                        return self._transform_excel_content(
                            parsed_data, bank_name, quarter
                        )
                    else:
                        # Other structured content
                        return self._transform_structured_content(
                            parsed_data, bank_name, quarter
                        )
                elif isinstance(parsed_data['content'], list):
                    # List of records (JSON, etc.)
                    return self._transform_list_content(
                        parsed_data, bank_name, quarter
                    )
            
            # Fallback for unknown formats
            logger.warning(f"Unknown content format in parsed data: {type(parsed_data.get('content'))}")
            return self._transform_fallback(parsed_data, bank_name, quarter)
            
        except Exception as e:
            logger.error(f"Error transforming parsed data: {e}")
            raise
    
    def _transform_text_content(
        self, 
        parsed_data: Dict[str, Any], 
        bank_name: str, 
        quarter: str
    ) -> List[Dict[str, Any]]:
        """Transform simple text content to NLP schema.
        
        Args:
            parsed_data: Parsed data with text content
            bank_name: Bank name
            quarter: Quarter identifier
            
        Returns:
            List of sentence-level records
        """
        content = parsed_data.get('content', '')
        if not content:
            return []
        
        # Split content into sentences
        sentences = sent_tokenize(content)
        
        records = []
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            # Create base record
            record = self._create_base_record(
                bank_name=bank_name,
                quarter=quarter,
                file_path=parsed_data.get('file_path', ''),
                document_type=parsed_data.get('document_type', 'unknown'),
                sentence_id=i + 1,
                text=sentence.strip()
            )
            
            # Add speaker information if available
            speaker = self._extract_speaker_from_sentence(sentence)
            record['speaker_norm'] = speaker
            record['analyst_utterance'] = self._is_analyst_utterance(speaker)
            
            records.append(record)
        
        return records
    
    def _transform_excel_content(
        self, 
        parsed_data: Dict[str, Any], 
        bank_name: str, 
        quarter: str
    ) -> List[Dict[str, Any]]:
        """Transform Excel content to NLP schema.
        
        Args:
            parsed_data: Parsed Excel data
            bank_name: Bank name
            quarter: Quarter identifier
            
        Returns:
            List of records from Excel data
        """
        records = []
        tables = parsed_data.get('content', {}).get('tables', {})
        
        sentence_id = 1
        
        for sheet_name, table_data in tables.items():
            if 'error' in table_data:
                logger.warning(f"Skipping sheet {sheet_name} due to error: {table_data['error']}")
                continue
            
            # Convert table data to text descriptions
            table_records = self._excel_table_to_text(
                table_data, sheet_name, bank_name, quarter, 
                parsed_data.get('file_path', ''), 
                parsed_data.get('document_type', 'supplement'),
                sentence_id
            )
            
            records.extend(table_records)
            sentence_id += len(table_records)
        
        return records
    
    def _transform_structured_content(
        self, 
        parsed_data: Dict[str, Any], 
        bank_name: str, 
        quarter: str
    ) -> List[Dict[str, Any]]:
        """Transform other structured content to NLP schema.
        
        Args:
            parsed_data: Parsed structured data
            bank_name: Bank name
            quarter: Quarter identifier
            
        Returns:
            List of records
        """
        # Handle pages from PDF content
        if 'pages' in parsed_data.get('content', {}):
            return self._transform_pdf_pages(parsed_data, bank_name, quarter)
        
        # Generic structured content handling
        content = parsed_data.get('content', {})
        text_content = str(content)
        
        return self._transform_text_content(
            {**parsed_data, 'content': text_content}, 
            bank_name, 
            quarter
        )
    
    def _transform_pdf_pages(
        self, 
        parsed_data: Dict[str, Any], 
        bank_name: str, 
        quarter: str
    ) -> List[Dict[str, Any]]:
        """Transform PDF pages to NLP schema.
        
        Args:
            parsed_data: Parsed PDF data with pages
            bank_name: Bank name
            quarter: Quarter identifier
            
        Returns:
            List of sentence-level records
        """
        pages = parsed_data.get('content', {}).get('pages', [])
        records = []
        sentence_id = 1
        
        for page in pages:
            page_text = page.get('text', '')
            if not page_text.strip():
                continue
            
            # Split page text into sentences
            sentences = sent_tokenize(page_text)
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                
                record = self._create_base_record(
                    bank_name=bank_name,
                    quarter=quarter,
                    file_path=parsed_data.get('file_path', ''),
                    document_type=parsed_data.get('document_type', 'unknown'),
                    sentence_id=sentence_id,
                    text=sentence.strip()
                )
                
                # Add page information
                record['page_number'] = page.get('page_number', 0)
                
                # Extract speaker if this is a transcript
                speaker = self._extract_speaker_from_sentence(sentence)
                record['speaker_norm'] = speaker
                record['analyst_utterance'] = self._is_analyst_utterance(speaker)
                
                records.append(record)
                sentence_id += 1
        
        return records
    
    def _transform_list_content(
        self, 
        parsed_data: Dict[str, Any], 
        bank_name: str, 
        quarter: str
    ) -> List[Dict[str, Any]]:
        """Transform list content to NLP schema.
        
        Args:
            parsed_data: Parsed data with list content
            bank_name: Bank name
            quarter: Quarter identifier
            
        Returns:
            List of records
        """
        content_list = parsed_data.get('content', [])
        records = []
        
        for i, item in enumerate(content_list):
            if isinstance(item, dict):
                text = item.get('text', str(item))
                speaker = item.get('speaker', 'UNKNOWN')
                timestamp = item.get('timestamp', '')
            else:
                text = str(item)
                speaker = 'UNKNOWN'
                timestamp = ''
            
            if not text.strip():
                continue
            
            record = self._create_base_record(
                bank_name=bank_name,
                quarter=quarter,
                file_path=parsed_data.get('file_path', ''),
                document_type=parsed_data.get('document_type', 'unknown'),
                sentence_id=i + 1,
                text=text.strip()
            )
            
            record['speaker_norm'] = self._normalize_speaker(speaker)
            record['analyst_utterance'] = self._is_analyst_utterance(speaker)
            
            if timestamp:
                record['timestamp_iso'] = timestamp
                record['timestamp_epoch'] = self._parse_timestamp(timestamp)
            
            records.append(record)
        
        return records
    
    def _transform_fallback(
        self, 
        parsed_data: Dict[str, Any], 
        bank_name: str, 
        quarter: str
    ) -> List[Dict[str, Any]]:
        """Fallback transformation for unknown formats.
        
        Args:
            parsed_data: Parsed data
            bank_name: Bank name
            quarter: Quarter identifier
            
        Returns:
            List with single record
        """
        # Convert entire parsed data to string
        text_content = str(parsed_data.get('content', ''))
        
        if not text_content.strip():
            return []
        
        record = self._create_base_record(
            bank_name=bank_name,
            quarter=quarter,
            file_path=parsed_data.get('file_path', ''),
            document_type=parsed_data.get('document_type', 'unknown'),
            sentence_id=1,
            text=text_content[:1000]  # Truncate if too long
        )
        
        return [record]
    
    def _create_base_record(
        self,
        bank_name: str,
        quarter: str,
        file_path: str,
        document_type: str,
        sentence_id: int,
        text: str
    ) -> Dict[str, Any]:
        """Create a base record conforming to NLP schema.
        
        Args:
            bank_name: Bank name
            quarter: Quarter identifier
            file_path: Source file path
            document_type: Type of document
            sentence_id: Sentence identifier
            text: Text content
            
        Returns:
            Base record dictionary
        """
        # Generate call_id from bank and quarter
        call_id = f"{bank_name}_{quarter}_{datetime.now().strftime('%Y%m%d')}"
        
        # Determine source type
        source_type = self._map_document_type_to_source_type(document_type)
        
        return {
            # Core metadata
            'bank_name': bank_name,
            'quarter': quarter,
            'call_id': call_id,
            
            # Source information
            'source_type': source_type,
            'file_path': file_path,
            
            # Timestamps
            'timestamp_epoch': None,
            'timestamp_iso': None,
            
            # Speaker information (defaults)
            'speaker_norm': 'UNKNOWN',
            'analyst_utterance': False,
            
            # Sentence-level information
            'sentence_id': sentence_id,
            'text': text,
            
            # NLP-specific fields (to be filled by NLP processors)
            'sentence_length': len(text),
            'word_count': len(text.split()),
            'sentiment_score': None,
            'sentiment_label': None,
            'key_phrases': None,
            'named_entities': None,
            
            # Topic modeling (to be filled by topic modeler)
            'topic_labels': None,
            'topic_scores': None,
            
            # Metadata
            'processing_date': datetime.now(),
            'processing_version': '1.0.0'
        }
    
    def _excel_table_to_text(
        self,
        table_data: Dict[str, Any],
        sheet_name: str,
        bank_name: str,
        quarter: str,
        file_path: str,
        document_type: str,
        start_sentence_id: int
    ) -> List[Dict[str, Any]]:
        """Convert Excel table data to text descriptions.
        
        Args:
            table_data: Table data from Excel parser
            sheet_name: Name of the Excel sheet
            bank_name: Bank name
            quarter: Quarter identifier
            file_path: Source file path
            document_type: Document type
            start_sentence_id: Starting sentence ID
            
        Returns:
            List of text records describing the table
        """
        records = []
        data_rows = table_data.get('data', [])
        columns = [col['name'] for col in table_data.get('columns', [])]
        
        if not data_rows or not columns:
            return records
        
        sentence_id = start_sentence_id
        
        # Create summary description
        summary_text = f"Sheet '{sheet_name}' contains {len(data_rows)} rows and {len(columns)} columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}."
        
        summary_record = self._create_base_record(
            bank_name=bank_name,
            quarter=quarter,
            file_path=file_path,
            document_type=document_type,
            sentence_id=sentence_id,
            text=summary_text
        )
        records.append(summary_record)
        sentence_id += 1
        
        # Convert significant rows to text (limit to avoid too much data)
        max_rows = min(10, len(data_rows))
        for i, row in enumerate(data_rows[:max_rows]):
            # Create text description of the row
            row_text = self._row_to_text(row, columns)
            if row_text:
                row_record = self._create_base_record(
                    bank_name=bank_name,
                    quarter=quarter,
                    file_path=file_path,
                    document_type=document_type,
                    sentence_id=sentence_id,
                    text=row_text
                )
                records.append(row_record)
                sentence_id += 1
        
        return records
    
    def _row_to_text(self, row: Dict[str, Any], columns: List[str]) -> str:
        """Convert a table row to text description.
        
        Args:
            row: Row data dictionary
            columns: Column names
            
        Returns:
            Text description of the row
        """
        # Focus on non-null, meaningful values
        meaningful_items = []
        
        for col in columns[:5]:  # Limit to first 5 columns
            value = row.get(col)
            if value is not None and str(value).strip():
                # Format the value appropriately
                if isinstance(value, (int, float)):
                    if abs(value) > 1000000:
                        formatted_value = f"{value/1000000:.1f}M"
                    elif abs(value) > 1000:
                        formatted_value = f"{value/1000:.1f}K"
                    else:
                        formatted_value = str(value)
                else:
                    formatted_value = str(value)[:50]  # Truncate long strings
                
                meaningful_items.append(f"{col}: {formatted_value}")
        
        if meaningful_items:
            return "; ".join(meaningful_items) + "."
        return ""
    
    def _extract_speaker_from_sentence(self, sentence: str) -> str:
        """Extract speaker name from sentence if present.
        
        Args:
            sentence: Text sentence
            
        Returns:
            Speaker name or 'UNKNOWN'
        """
        # Look for speaker patterns like "John Smith:" or "SPEAKER:"
        speaker_pattern = r'^([A-Z][a-zA-Z\s]+?):\s*'
        match = re.match(speaker_pattern, sentence.strip())
        
        if match:
            return self._normalize_speaker(match.group(1))
        
        return 'UNKNOWN'
    
    def _normalize_speaker(self, speaker: str) -> str:
        """Normalize speaker name.
        
        Args:
            speaker: Raw speaker name
            
        Returns:
            Normalized speaker name
        """
        if not speaker or speaker.strip().lower() in ['unknown', 'none', '']:
            return 'UNKNOWN'
        
        # Clean up the speaker name
        normalized = speaker.strip().title()
        
        # Remove common prefixes/suffixes
        prefixes = ['Mr.', 'Ms.', 'Mrs.', 'Dr.', 'Prof.']
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):].strip()
        
        return normalized if normalized else 'UNKNOWN'
    
    def _is_analyst_utterance(self, speaker: str) -> bool:
        """Determine if speaker is an analyst.
        
        Args:
            speaker: Speaker name
            
        Returns:
            True if speaker is likely an analyst
        """
        if not speaker or speaker == 'UNKNOWN':
            return False
        
        # Simple heuristic - analysts often have company names or "Analyst" in their title
        analyst_indicators = ['analyst', 'research', 'equity', 'investment', 'bank', 'securities']
        speaker_lower = speaker.lower()
        
        return any(indicator in speaker_lower for indicator in analyst_indicators)
    
    def _map_document_type_to_source_type(self, document_type: str) -> str:
        """Map document type to source type for schema.
        
        Args:
            document_type: Document type from parser
            
        Returns:
            Source type for schema
        """
        mapping = {
            'transcript': 'earnings_call',
            'presentation': 'earnings_presentation',
            'supplement': 'financial_supplement',
            'results': 'financial_results',
            'financial_statements': 'financial_statements',
            'other': 'other'
        }
        
        return mapping.get(document_type, 'other')
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[int]:
        """Parse timestamp string to epoch time.
        
        Args:
            timestamp_str: Timestamp string
            
        Returns:
            Epoch timestamp or None
        """
        try:
            # Try common timestamp formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d',
                '%H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    return int(dt.timestamp())
                except ValueError:
                    continue
            
            return None
        except Exception:
            return None


def transform_to_nlp_schema(
    parsed_data: Dict[str, Any], 
    bank_name: str, 
    quarter: str,
    config: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """Convenience function to transform parsed data to NLP schema.
    
    Args:
        parsed_data: Output from any parser
        bank_name: Bank name
        quarter: Quarter identifier
        config: Optional configuration
        
    Returns:
        List of records conforming to NLP schema
    """
    transformer = SchemaTransformer(config)
    return transformer.transform_parsed_data(parsed_data, bank_name, quarter)