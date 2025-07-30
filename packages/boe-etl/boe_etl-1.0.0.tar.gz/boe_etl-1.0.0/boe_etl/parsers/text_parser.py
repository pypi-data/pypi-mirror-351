"""
Text file parsing functionality for the ETL pipeline.
Specialized for transcript files with speaker identification.
"""
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from .base_parser import BaseParser

logger = logging.getLogger(__name__)


class TextParser(BaseParser):
    """Parser for text files, especially transcripts."""
    
    def __init__(self, bank: str, quarter: str):
        """Initialize the text parser.
        
        Args:
            bank: Name of the bank
            quarter: Quarter identifier (e.g., 'Q1_2025')
        """
        super().__init__(bank, quarter)
        self.supported_formats = {'.txt'}
        
        # Speaker identification patterns
        self.speaker_patterns = [
            r'^([A-Z][a-zA-Z\s\-\.]+?):\s*(.+)$',  # "John Smith: text"
            r'^([A-Z]+):\s*(.+)$',                  # "SPEAKER: text"
            r'^([A-Z][a-zA-Z\s]+)\s*-\s*(.+)$',    # "John Smith - text"
            r'^\[([^\]]+)\]:\s*(.+)$',              # "[Speaker Name]: text"
            r'^(\w+\s+\w+):\s*(.+)$',               # "First Last: text"
        ]
        
        # Timestamp patterns
        self.timestamp_patterns = [
            r'\[(\d{1,2}:\d{2}:\d{2})\]',           # [HH:MM:SS]
            r'\[(\d{1,2}:\d{2})\]',                 # [HH:MM]
            r'(\d{1,2}:\d{2}:\d{2})',               # HH:MM:SS
            r'(\d{1,2}:\d{2})',                     # HH:MM
        ]
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse a text file and extract its content.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dictionary containing the parsed data with standardized structure
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")
        
        # Infer document type from filename
        document_type = self._infer_document_type(file_path.name)
        
        result = {
            'bank': self.bank,
            'quarter': self.quarter,
            'file_path': str(file_path),
            'document_type': document_type,
            'content': '',
            'metadata': self.get_metadata(file_path),
            'speakers': [],
            'segments': []
        }
        
        try:
            # Read the text file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logger.warning(f"Empty text file: {file_path}")
                return result
            
            # Parse based on document type
            if document_type == 'transcript':
                result = self._parse_transcript(content, result)
            else:
                result = self._parse_generic_text(content, result)
            
            # Add parsing metadata
            result['metadata'].update({
                'total_lines': len(content.splitlines()),
                'total_characters': len(content),
                'total_words': len(content.split()),
                'speakers_detected': len(result['speakers']),
                'segments_detected': len(result['segments'])
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing text file {file_path}: {str(e)}")
            raise
    
    def _parse_transcript(self, content: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse transcript content with speaker identification.
        
        Args:
            content: Raw text content
            result: Result dictionary to update
            
        Returns:
            Updated result dictionary
        """
        lines = content.splitlines()
        segments = []
        speakers = set()
        current_speaker = None
        current_text = []
        current_timestamp = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Try to extract timestamp
            timestamp = self._extract_timestamp(line)
            if timestamp:
                current_timestamp = timestamp
                # Remove timestamp from line
                line = self._remove_timestamp(line)
                if not line.strip():
                    continue
            
            # Try to identify speaker
            speaker_match = self._identify_speaker(line)
            
            if speaker_match:
                # Save previous segment if exists
                if current_speaker and current_text:
                    segments.append({
                        'speaker': current_speaker,
                        'text': ' '.join(current_text).strip(),
                        'timestamp': current_timestamp,
                        'line_start': line_num - len(current_text),
                        'line_end': line_num - 1
                    })
                
                # Start new segment
                current_speaker = speaker_match['speaker']
                current_text = [speaker_match['text']] if speaker_match['text'] else []
                speakers.add(current_speaker)
                
            else:
                # Continue current speaker's text
                if current_speaker:
                    current_text.append(line)
                else:
                    # No speaker identified, treat as generic text
                    segments.append({
                        'speaker': 'UNKNOWN',
                        'text': line,
                        'timestamp': current_timestamp,
                        'line_start': line_num,
                        'line_end': line_num
                    })
                    speakers.add('UNKNOWN')
        
        # Save final segment
        if current_speaker and current_text:
            segments.append({
                'speaker': current_speaker,
                'text': ' '.join(current_text).strip(),
                'timestamp': current_timestamp,
                'line_start': len(lines) - len(current_text) + 1,
                'line_end': len(lines)
            })
        
        # Update result
        result['segments'] = segments
        result['speakers'] = list(speakers)
        result['content'] = self._reconstruct_content(segments)
        
        return result
    
    def _parse_generic_text(self, content: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse generic text content.
        
        Args:
            content: Raw text content
            result: Result dictionary to update
            
        Returns:
            Updated result dictionary
        """
        # For generic text, just store the content
        result['content'] = content
        result['segments'] = [{
            'speaker': 'UNKNOWN',
            'text': content,
            'timestamp': None,
            'line_start': 1,
            'line_end': len(content.splitlines())
        }]
        result['speakers'] = ['UNKNOWN']
        
        return result
    
    def _identify_speaker(self, line: str) -> Optional[Dict[str, str]]:
        """Identify speaker from a line of text.
        
        Args:
            line: Line of text
            
        Returns:
            Dictionary with speaker and text, or None if no speaker found
        """
        for pattern in self.speaker_patterns:
            match = re.match(pattern, line.strip())
            if match:
                speaker = match.group(1).strip()
                text = match.group(2).strip() if len(match.groups()) > 1 else ''
                
                # Clean up speaker name
                speaker = self._normalize_speaker_name(speaker)
                
                return {
                    'speaker': speaker,
                    'text': text
                }
        
        return None
    
    def _normalize_speaker_name(self, speaker: str) -> str:
        """Normalize speaker name.
        
        Args:
            speaker: Raw speaker name
            
        Returns:
            Normalized speaker name
        """
        # Remove common prefixes and suffixes
        speaker = speaker.strip()
        
        # Remove brackets if present
        speaker = re.sub(r'[\[\]()]', '', speaker)
        
        # Remove common titles
        titles = ['Mr.', 'Ms.', 'Mrs.', 'Dr.', 'Prof.', 'CEO', 'CFO', 'CTO']
        for title in titles:
            speaker = re.sub(rf'\b{re.escape(title)}\b', '', speaker, flags=re.IGNORECASE)
        
        # Clean up whitespace and convert to title case
        speaker = ' '.join(speaker.split()).title()
        
        return speaker if speaker else 'UNKNOWN'
    
    def _extract_timestamp(self, line: str) -> Optional[str]:
        """Extract timestamp from a line.
        
        Args:
            line: Line of text
            
        Returns:
            Timestamp string or None
        """
        for pattern in self.timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        
        return None
    
    def _remove_timestamp(self, line: str) -> str:
        """Remove timestamp from a line.
        
        Args:
            line: Line of text
            
        Returns:
            Line with timestamp removed
        """
        for pattern in self.timestamp_patterns:
            line = re.sub(pattern, '', line)
        
        return line.strip()
    
    def _reconstruct_content(self, segments: List[Dict[str, Any]]) -> str:
        """Reconstruct content from segments.
        
        Args:
            segments: List of text segments
            
        Returns:
            Reconstructed content string
        """
        content_parts = []
        
        for segment in segments:
            speaker = segment.get('speaker', 'UNKNOWN')
            text = segment.get('text', '')
            timestamp = segment.get('timestamp', '')
            
            if timestamp:
                content_parts.append(f"[{timestamp}] {speaker}: {text}")
            else:
                content_parts.append(f"{speaker}: {text}")
        
        return '\n'.join(content_parts)
    
    def _infer_document_type(self, filename: str) -> str:
        """Infer the document type from the filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            Inferred document type
        """
        filename = filename.lower()
        if any(term in filename for term in ['transcript', 'call', 'earnings']):
            return 'transcript'
        elif any(term in filename for term in ['presentation', 'slide']):
            return 'presentation'
        elif any(term in filename for term in ['supplement', 'financial']):
            return 'supplement'
        elif any(term in filename for term in ['result', 'statement']):
            return 'results'
        return 'other'


def parse_text(bank: str, quarter: str, file_path: Path, document_type: str = "unknown") -> Dict[str, Any]:
    """
    Parse a text file and extract its content.
    
    This is a convenience function that creates a TextParser instance.
    For new code, it's recommended to use the TextParser class directly.
    
    Args:
        bank: Name of the bank
        quarter: Quarter identifier (e.g., 'Q1_2025')
        file_path: Path to the text file
        document_type: Type of document (e.g., 'transcript', 'presentation')
                      If "unknown", will attempt to infer from filename
    
    Returns:
        Dictionary containing the parsed data
    """
    parser = TextParser(bank, quarter)
    result = parser.parse(file_path)
    
    # For backward compatibility
    if document_type != "unknown" and document_type != result['document_type']:
        result['document_type'] = document_type
        
    return result


def test_parse_text():
    """Test function for the text parser"""
    import tempfile
    from pathlib import Path
    
    # Create a sample transcript file for testing
    sample_transcript = """[10:00:00] John Smith: Good morning everyone, welcome to our Q1 earnings call.

[10:00:15] Jane Doe: Thank you John. Let me start with our financial highlights.
Our revenue increased by 15% compared to last quarter.

[10:01:00] Analyst Mike: Can you provide more details on the revenue growth?

Jane Doe: Certainly. The growth was primarily driven by our new product launches
and improved market penetration in the Asia-Pacific region.

[10:02:30] John Smith: I'd like to add that our operational efficiency has also improved significantly.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_transcript.txt', delete=False) as tmp:
        tmp.write(sample_transcript)
        test_file = Path(tmp.name)
    
    try:
        parser = TextParser('test_bank', 'Q1_2025')
        result = parser.parse(test_file)
        print("Text parse test successful!")
        print(f"Document type: {result['document_type']}")
        print(f"Speakers found: {result['speakers']}")
        print(f"Segments: {len(result['segments'])}")
        return True
    except Exception as e:
        print(f"Text parse test failed: {str(e)}")
        return False
    finally:
        test_file.unlink()  # Clean up


if __name__ == "__main__":
    test_parse_text()