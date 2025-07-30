#!/usr/bin/env python3
"""
BoE ETL NLP Module
==================

Natural Language Processing functionality for the BoE ETL package.
Provides NLP features extraction and text analysis capabilities.
"""

import pandas as pd
import re
from typing import List, Dict, Any, Optional
import logging

from .schema_transformer import SchemaTransformer


class NLPProcessor:
    """
    NLP processor for financial document analysis.
    
    Provides methods for extracting financial terms, classifying topics,
    and adding NLP features to processed data.
    """
    
    def __init__(self):
        """Initialize the NLP processor."""
        self.transformer = SchemaTransformer()
        self.logger = logging.getLogger(__name__)
    
    def add_nlp_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add comprehensive NLP features to a DataFrame.
        
        Args:
            df: Input DataFrame with text data
            
        Returns:
            DataFrame with added NLP features
        """
        return self.transformer.add_nlp_features(df)
    
    def extract_financial_terms(self, text: str) -> List[str]:
        """
        Extract financial terms from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of financial terms found in the text
        """
        if not text or pd.isna(text):
            return []
        
        return self.transformer._extract_financial_terms(text)
    
    def extract_financial_figures(self, text: str) -> List[str]:
        """
        Extract financial figures from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of financial figures found in the text
        """
        if not text or pd.isna(text):
            return []
        
        return self.transformer._extract_financial_figures(text)
    
    def classify_topic(self, text: str) -> str:
        """
        Classify the primary topic of text.
        
        Args:
            text: Input text to classify
            
        Returns:
            Primary topic classification
        """
        if not text or pd.isna(text):
            return 'Unknown'
        
        return self.transformer._classify_primary_topic(text)
    
    def detect_data_type(self, text: str) -> str:
        """
        Detect whether text contains actual or projection data.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Data type classification ('Actual', 'Projection', 'Mixed', 'Unknown')
        """
        if not text or pd.isna(text):
            return 'Unknown'
        
        return self.transformer._classify_data_type(text)
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of financial text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not text or pd.isna(text):
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'positive_indicators': [],
                'negative_indicators': []
            }
        
        # Simple sentiment analysis based on financial keywords
        positive_terms = [
            'growth', 'increase', 'strong', 'positive', 'improvement', 'gain',
            'profit', 'success', 'expansion', 'outperform', 'exceed', 'beat'
        ]
        
        negative_terms = [
            'decline', 'decrease', 'weak', 'negative', 'loss', 'drop',
            'concern', 'challenge', 'risk', 'underperform', 'miss', 'fall'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for term in positive_terms if term in text_lower)
        negative_count = sum(1 for term in negative_terms if term in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_indicators': [term for term in positive_terms if term in text_lower],
            'negative_indicators': [term for term in negative_terms if term in text_lower]
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from financial text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with extracted entities by type
        """
        if not text or pd.isna(text):
            return {
                'companies': [],
                'people': [],
                'locations': [],
                'financial_metrics': [],
                'dates': []
            }
        
        entities = {
            'companies': [],
            'people': [],
            'locations': [],
            'financial_metrics': [],
            'dates': []
        }
        
        # Extract financial metrics (simplified)
        metric_patterns = [
            r'\b(?:revenue|earnings|profit|loss|margin|ratio|rate)\b',
            r'\b(?:EPS|ROE|ROA|P/E|EBITDA|GDP|CPI)\b',
            r'\b(?:basis points?|bps)\b'
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['financial_metrics'].extend(matches)
        
        # Extract dates (simplified)
        date_patterns = [
            r'\b(?:Q[1-4])\s+(?:20\d{2})\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(?:20\d{2})\b',
            r'\b(?:20\d{2})\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['dates'].extend(matches)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        Get basic text statistics.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with text statistics
        """
        if not text or pd.isna(text):
            return {
                'word_count': 0,
                'sentence_count': 0,
                'character_count': 0,
                'avg_word_length': 0.0,
                'financial_term_density': 0.0
            }
        
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        financial_terms = self.extract_financial_terms(text)
        
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        character_count = len(text)
        avg_word_length = sum(len(word) for word in words) / max(word_count, 1)
        financial_term_density = len(financial_terms) / max(word_count, 1)
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'character_count': character_count,
            'avg_word_length': round(avg_word_length, 2),
            'financial_term_density': round(financial_term_density, 4)
        }
    
    def process_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Process a batch of texts and return comprehensive NLP analysis.
        
        Args:
            texts: List of texts to process
            
        Returns:
            List of dictionaries with NLP analysis for each text
        """
        results = []
        
        for text in texts:
            analysis = {
                'text': text,
                'financial_terms': self.extract_financial_terms(text),
                'financial_figures': self.extract_financial_figures(text),
                'primary_topic': self.classify_topic(text),
                'data_type': self.detect_data_type(text),
                'sentiment': self.analyze_sentiment(text),
                'entities': self.extract_entities(text),
                'statistics': self.get_text_statistics(text)
            }
            results.append(analysis)
        
        return results


# Convenience functions
def analyze_text(text: str) -> Dict[str, Any]:
    """
    Quick function to analyze a single text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with comprehensive NLP analysis
    """
    processor = NLPProcessor()
    return processor.process_batch([text])[0]


def analyze_dataframe(df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
    """
    Quick function to add NLP features to a DataFrame.
    
    Args:
        df: Input DataFrame
        text_column: Name of the column containing text
        
    Returns:
        DataFrame with added NLP features
    """
    processor = NLPProcessor()
    
    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found in DataFrame")
    
    return processor.add_nlp_features(df)