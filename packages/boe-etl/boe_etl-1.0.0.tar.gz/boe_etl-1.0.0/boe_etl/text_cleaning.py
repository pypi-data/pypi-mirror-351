import re
import string
import logging
from typing import Dict, List, Optional, Any, Union, Type, Callable
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
import spacy
from spacy.lang.en import English
import json
from pathlib import Path
from .config import ConfigManager

# Initialize NLP models
nlp = spacy.load('en_core_web_sm')
lemmatizer = WordNetLemmatizer()

# Load stop words
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

STOP_WORDS = set(stopwords.words('english'))

# Load custom fillers and replacements
FILLERS_FILE = Path(__file__).parent / 'data' / 'fillers.json'
if FILLERS_FILE.exists():
    with open(FILLERS_FILE, 'r') as f:
        CUSTOM_FILLERS = json.load(f)
else:
    CUSTOM_FILLERS = {}

class TextCleaner:
    """Advanced text cleaning and normalization class"""
    def __init__(self, config: Optional[Dict] = None):
        """Initialize text cleaner with configuration"""
        self.config_manager = ConfigManager()
        self.config = config or self.config_manager.get_config().text_cleaning
        
        # Set up default values for any potentially missing attributes
        self.default_special_chars = ['%', '$', '£', '€', '#', '@', '&', '/', '-', '_', '+', '=']
        self.preserve_special_chars = getattr(self.config, 'preserve_special_chars', self.default_special_chars)
        self.remove_numbers = getattr(self.config, 'remove_numbers', False)
        self.preserve_numbers_with_units = getattr(self.config, 'preserve_numbers_with_units', True)
        
        # Load financial terms if enabled (with safe attribute check)
        self.financial_terms = set()
        if hasattr(self.config, 'use_financial_terms') and getattr(self.config, 'use_financial_terms', False):
            self._load_financial_terms()
        
        # Compile regex patterns
        self.patterns = {
            'numbers': re.compile(r'\d+'),
            'numbers_with_units': re.compile(r'\d+[\w%$£€/]+'),
            'punctuation': re.compile(r'[\s' + re.escape("".join(set(string.punctuation) - set(self.preserve_special_chars))) + r']+'),
            'special_chars': re.compile(r'[^' + re.escape("".join(self.preserve_special_chars)) + r'\w\s]'),
            'whitespace': re.compile(r'\s+'),
            'urls': re.compile(r'https?://\S+|www\.\S+'),
            'emails': re.compile(r'\S+@\S+'),
            'extra_whitespace': re.compile(r'\s+'),
            'fillers': self._compile_fillers()
        }
        
        # Compile regex for financial terms
        if self.financial_terms:
            self.patterns['financial_terms'] = re.compile(
                r'\b(' + '|'.join(map(re.escape, self.financial_terms)) + r')\b', 
                flags=re.IGNORECASE
            )
            
    def _load_financial_terms(self):
        """Load financial terms from a predefined list"""
        financial_terms_file = Path(__file__).parent / 'data' / 'financial_terms.txt'
        try:
            if financial_terms_file.exists():
                with open(financial_terms_file, 'r', encoding='utf-8') as f:
                    self.financial_terms = {line.strip().lower() for line in f if line.strip()}
        except Exception as e:
            logging.warning(f"Failed to load financial terms: {e}")
            self.financial_terms = set()
        
    def _compile_fillers(self) -> re.Pattern:
        """Compile regex pattern for fillers"""
        fillers = set(CUSTOM_FILLERS.keys())
        if self.config.remove_stopwords:
            fillers.update(STOP_WORDS)
        return re.compile(r'\b(' + '|'.join(map(re.escape, fillers)) + r')\b', re.IGNORECASE)
    
    def _get_wordnet_pos(self, word: str) -> str:
        """Map POS tag to WordNet POS tag"""
        tag = nltk.pos_tag([word], lang='en')[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                   "N": wordnet.NOUN,
                   "V": wordnet.VERB,
                   "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)
    
    def _lemmatize_text(self, text: str) -> str:
        """Lemmatize text using WordNet"""
        # Simplified lemmatization to avoid POS tagging issues
        words = word_tokenize(text)
        lemmatized = []
        for word in words:
            # Just use the default noun POS
            lemmatized.append(lemmatizer.lemmatize(word))
        return ' '.join(lemmatized)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text using spaCy"""
        doc = nlp(text)
        normalized = []
        for token in doc:
            if not token.is_stop and not token.is_punct:
                normalized.append(token.lemma_.lower())
        return ' '.join(normalized)
    
    def get_parameters(self) -> Dict:
        """Get the text cleaning parameters"""
        return {
            "min_word_length": getattr(self.config, 'min_word_length', 2),
            "max_word_length": getattr(self.config, 'max_word_length', 50),
            "remove_numbers": self.remove_numbers,
            "remove_punctuation": getattr(self.config, 'remove_punctuation', False),
            "remove_special_chars": getattr(self.config, 'remove_special_chars', False),
            "remove_stopwords": getattr(self.config, 'remove_stopwords', False)
        }
    
    def clean_text(self, text: str) -> str:
        """Clean text with all configured options"""
        if not text or not isinstance(text, str):
            return ""
            
        try:
            # Convert to string and normalize unicode
            text = str(text).strip()
            
            # Early return for empty text after conversion
            if not text:
                return ""
                
            # Replace common HTML entities and other special characters
            text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            
            # Remove URLs and email addresses
            text = self.patterns['urls'].sub('', text)
            text = self.patterns['emails'].sub('', text)
            
            # Replace fillers and common abbreviations
            for pattern, replacement in self.config.replace_fillers.items():
                text = text.replace(pattern, replacement)
            
            # Preserve numbers with units (e.g., 10%, $1M) if configured
            preserved_numbers = {}
            if self.preserve_numbers_with_units and not self.remove_numbers:
                for i, match in enumerate(self.patterns['numbers_with_units'].finditer(text)):
                    placeholder = f"__NUM_{i}__"
                    preserved_numbers[placeholder] = match.group(0)
                    text = text[:match.start()] + ' ' + placeholder + ' ' + text[match.end():]
            
            # Remove punctuation if configured (while preserving special chars)
            if getattr(self.config, 'remove_punctuation', False):
                text = self.patterns['punctuation'].sub(' ', text)
            
            # Handle special characters
            if getattr(self.config, 'remove_special_chars', False):
                text = self.patterns['special_chars'].sub(' ', text)
            
            # Normalize whitespace and case
            text = self.patterns['extra_whitespace'].sub(' ', text).strip().lower()
            
            # Restore preserved numbers
            for placeholder, number in preserved_numbers.items():
                text = text.replace(placeholder, number)
            
            # Advanced NLP processing
            if getattr(self.config, 'lemmatize', True):  # Default to True if not present
                try:
                    doc = nlp(text)
                    lemmatized = []
                    for token in doc:
                        # Skip stopwords if configured
                        if getattr(self.config, 'remove_stopwords', False) and token.is_stop:
                            continue
                            
                        # Handle financial terms specially
                        if self.financial_terms and token.text.lower() in self.financial_terms:
                            lemmatized.append(token.text.lower())
                        else:
                            # Use lemma for non-financial terms
                            lemma = token.lemma_.lower().strip()
                            min_len = getattr(self.config, 'min_word_length', 2)
                            max_len = getattr(self.config, 'max_word_length', 50)
                            if len(lemma) >= min_len and len(lemma) <= max_len:
                                lemmatized.append(lemma)
                    
                    text = ' '.join(lemmatized)
                except Exception as e:
                    logging.warning(f"NLP processing failed: {e}")
                    # Fall back to simple tokenization
                    words = text.split()
                    words = [w for w in words 
                            if self.config.min_word_length <= len(w) <= self.config.max_word_length]
                    text = ' '.join(words)
            
            # Final cleanup
            text = ' '.join(text.split())  # Remove extra whitespace
            
            # Apply custom stopwords removal
            custom_stopwords = getattr(self.config, 'custom_stopwords', [])
            if custom_stopwords:
                words = text.split()
                words = [w for w in words if w.lower() not in custom_stopwords]
                text = ' '.join(words)
            
            return text.strip()
            
        except Exception as e:
            logging.error(f"Error cleaning text: {e}")
            return ""
    
    def clean_and_split(self, text: str) -> List[str]:
        """Clean text and split into sentences"""
        sentences = sent_tokenize(text)
        cleaned_sentences = []
        for sentence in sentences:
            cleaned = self.clean_text(sentence)
            if cleaned:
                cleaned_sentences.append(cleaned)
        return cleaned_sentences

class SpeakerNormalizer:
    """Class for normalizing speaker names"""
    def __init__(self, config: Optional[Dict] = None):
        """Initialize speaker normalizer with configuration"""
        self.config = config or ConfigManager().get_config().speaker_normalization
        self.honorifics = set(self.config.honorifics)
        
    def _remove_honorifics(self, name: str) -> str:
        """Remove honorific titles from name"""
        words = name.split()
        return ' '.join(w for w in words if w.lower() not in self.honorifics)
    
    def _standardize_role_titles(self, title: str) -> str:
        """Standardize role titles"""
        title = title.lower()
        for original, standard in self.config.role_title_map.items():
            if original.lower() in title:
                return standard
        return title.title()
    
    def normalize_name(self, name: str) -> str:
        """Normalize speaker name"""
        if not name:
            return "UNKNOWN"
            
        name = name.strip()
        
        # Remove honorifics if configured
        if self.config.remove_honorifics:
            name = self._remove_honorifics(name)
        
        # Standardize role titles if configured
        if self.config.standardize_role_titles:
            name = self._standardize_role_titles(name)
        
        # Apply title case if configured
        if self.config.title_case:
            name = name.title()
        
        return name.strip()

def clean_transcript(transcript: Dict[str, str], config: Optional[Dict] = None) -> Dict[str, str]:
    """Clean an entire transcript dictionary"""
    text_cleaner = TextCleaner(config)
    speaker_normalizer = SpeakerNormalizer(config)
    
    cleaned_transcript = {}
    for speaker, text in transcript.items():
        normalized_speaker = speaker_normalizer.normalize_name(speaker)
        cleaned_text = text_cleaner.clean_text(text)
        cleaned_transcript[normalized_speaker] = cleaned_text
    
    return cleaned_transcript

def clean_and_split_records(records: List[Dict[str, str]], config: Optional[Dict] = None) -> List[Dict[str, str]]:
    """Clean and split multiple records"""
    text_cleaner = TextCleaner(config)
    speaker_normalizer = SpeakerNormalizer(config)
    
    cleaned_records = []
    for record in records:
        try:
            # Normalize speaker
            speaker = speaker_normalizer.normalize_name(record.get('speaker', ''))
            
            # Clean and split text
            text = record.get('text', '')
            sentences = text_cleaner.clean_and_split(text)
            
            # Create sentence-level records
            for sentence in sentences:
                if sentence:
                    cleaned_records.append({
                        'speaker': speaker,
                        'text': sentence,
                        'timestamp': record.get('timestamp', ''),
                        'sentence_id': f"{record.get('timestamp', '')}_{len(cleaned_records)}"
                    })
        except Exception as e:
            print(f"Error cleaning record: {e}")
            continue
    
    return cleaned_records
