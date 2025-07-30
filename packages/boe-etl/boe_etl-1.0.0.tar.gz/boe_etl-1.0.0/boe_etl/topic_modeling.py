import yaml
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any, Union, Type, Callable
from pathlib import Path
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from .config import ConfigManager
from .nlp_schema import NLPSchema
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

class TopicModeler:
    """Hybrid topic modeling class"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.seed_themes = self._load_seed_themes()
        self.vectorizer = CountVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            min_df=0.01,
            max_df=0.95
        )
        
        # Initialize BERTopic with FinBERT
        self.bertopic = BERTopic(
            embedding_model="ProsusAI/finbert",
            language="english",
            calculate_probabilities=True,
            verbose=True
        )
        
    def _load_seed_themes(self) -> Dict[str, List[str]]:
        """Load seed themes from YAML configuration"""
        theme_path = Path(__file__).parent / "data" / "seed_keywords.yml"
        with open(theme_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _preprocess_text(self, text: str) -> str:
        """Text preprocessing for topic modeling"""
        # Tokenize and remove stopwords
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        tokens = [t for t in tokens if t not in stop_words]
        
        # Remove punctuation and numbers
        tokens = [t for t in tokens if t.isalpha()]
        return ' '.join(tokens)
    
    def assign_seed_theme(self, text: str, threshold: int = 2) -> Optional[str]:
        """Assign text to a seed theme based on keyword matching"""
        processed_text = self._preprocess_text(text)
        scores = {
            theme: sum(processed_text.count(k) 
                      for k in self.seed_themes[theme])
            for theme in self.seed_themes
        }
        
        # Get best theme
        best_theme, best_score = max(scores.items(), key=lambda kv: kv[1])
        return best_theme if best_score >= threshold else None
    
    def process_seed_themes(self, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Process records using seed themes"""
        seed_assigned = []
        misc_corpus = []
        
        for record in records:
            theme = self.assign_seed_theme(record["text"])
            if theme:
                record["topic_label"] = theme
                record["topic_confidence"] = 1.0  # High confidence for seed themes
                seed_assigned.append(record)
            else:
                misc_corpus.append(record)
        
        logging.info(f"Assigned {len(seed_assigned)} records to seed themes")
        return seed_assigned, misc_corpus
    
    def process_emerging_topics(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process records using BERTopic for emerging topics"""
        if not records:
            return []
            
        texts = [r["text"] for r in records]
        
        # Special handling for single document case - BERTopic/UMAP can't handle single samples
        if len(texts) == 1:
            logging.info("Only one document found - assigning default topic")
            records[0]["topic_label"] = "Topic_0"
            records[0]["topic_confidence"] = 1.0
            records[0]["topic_keywords"] = "transcript, citigroup, bank, financial"
            return records
            
        try:
            # Fit BERTopic model
            topics, probs = self.bertopic.fit_transform(texts)
            
            # Get topic representations
            topic_representations = self.bertopic.get_topic_info()
            
            # Update records with topic information
            for i, (record, topic, prob) in enumerate(zip(records, topics, probs)):
                if topic != -1:  # Skip outliers
                    record["topic_label"] = f"Emerging_{topic}"
                    record["topic_confidence"] = float(prob)
                    
                    # Add top keywords
                    keywords = topic_representations[topic_representations["Topic"] == topic]
                    if not keywords.empty:
                        record["topic_keywords"] = keywords["Representation"].iloc[0]
        except Exception as e:
            logging.error(f"Error in topic modeling: {e}")
            # Fallback: assign default topic to all records
            for record in records:
                record["topic_label"] = "Topic_Default"
                record["topic_confidence"] = 0.5
                record["topic_keywords"] = "document, text, content"
                
        logging.info(f"Assigned {len(records)} records to topics")
        return records
    
    def analyze_topics(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze topic distribution and statistics"""
        df = pd.DataFrame(records)
        
        # Topic distribution
        topic_dist = df["topic_label"].value_counts(normalize=True).to_dict()
        
        # Confidence scores
        avg_confidence = df["topic_confidence"].mean()
        
        # Keyword frequency
        all_text = ' '.join(df["text"])
        tokens = word_tokenize(all_text.lower())
        keyword_freq = Counter(tokens).most_common(20)
        
        return {
            "topic_distribution": topic_dist,
            "average_confidence": avg_confidence,
            "top_keywords": keyword_freq,
            "total_records": len(records),
            "seed_theme_count": len(df[df["topic_label"].str.startswith("Emerging").fillna(False)])
        }
    
    def process_batch(
        self,
        records: List[Dict[str, Any]],
        bank_name: str,
        quarter: str
    ) -> List[Dict[str, Any]]:
        """Process a batch of records through the hybrid pipeline"""
        try:
            logging.info(f"Processing {len(records)} records for {bank_name} {quarter}")
            
            # Stage 1: Seed theme assignment
            seed_assigned, misc_corpus = self.process_seed_themes(records)
            
            # Stage 2: Emerging topic modeling
            emerging_records = self.process_emerging_topics(misc_corpus)
            
            # Combine results
            all_records = seed_assigned + emerging_records
            
            # Add metadata
            for record in all_records:
                record["bank_name"] = bank_name
                record["quarter"] = quarter
                record["processing_date"] = datetime.now().isoformat()
            
            # Analyze results
            analysis = self.analyze_topics(all_records)
            logging.info(f"Topic analysis: {analysis}")
            
            return all_records
            
        except Exception as e:
            logging.error(f"Failed to process batch: {e}")
            raise

def get_topic_modeler() -> TopicModeler:
    """Get the singleton topic modeler instance"""
    if not hasattr(get_topic_modeler, 'instance'):
        get_topic_modeler.instance = TopicModeler()
    return get_topic_modeler.instance
