#!/usr/bin/env python3
"""
fetch_and_parse.py

ETL pipeline to:
1. Fetch transcript & presentation files for each bank + quarter
2. Parse PDF/HTML/VTT into sentence-level records
3. Clean, normalize, and enrich with metadata
4. Write out partitioned Parquet files
5. Register each call in the SQLite catalog
"""

import os
import sqlite3
import argparse
import logging
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pdfplumber
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import pyarrow as pa
from typing import List, Dict, Optional, Tuple
import json
from urllib.parse import urlparse
from retry import retry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# CONFIGURATION
RAW_DIR = Path(os.getenv("RAW_DATA_DIR", "data/raw"))
CLEAN_DIR = Path(os.getenv("PROCESSED_DATA_DIR", "data/processed"))
DB_PATH = Path(os.getenv("DB_PATH", "db/earnings.db"))
LOG_PATH = Path(os.getenv("LOG_PATH", "logs/etl.log"))
PARQUET_OPT = {"engine": "pyarrow", "compression": "snappy"}
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Set up logging
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

class ETLException(Exception):
    """Base exception for ETL pipeline errors"""
    pass

class FetchError(ETLException):
    """Error during file fetching"""
    pass

class ParseError(ETLException):
    """Error during file parsing"""
    pass

class DatabaseError(ETLException):
    """Error during database operations"""
    pass

def validate_bank_name(bank: str) -> bool:
    """Validate bank name format"""
    if not bank or not isinstance(bank, str):
        raise ValueError("Bank name must be a non-empty string")
    return True

def validate_quarter(quarter: str) -> bool:
    """Validate quarter format (e.g., Q1_2023)"""
    if not isinstance(quarter, str) or not quarter.startswith("Q"):
        raise ValueError("Quarter must be in format QX_YYYY")
    try:
        q, year = quarter.split("_")
        if q not in [f"Q{i}" for i in range(1, 5)]:
            raise ValueError
        if not year.isdigit() or len(year) != 4:
            raise ValueError
    except ValueError:
        raise ValueError("Quarter must be in format QX_YYYY")
    return True

def initialize_database() -> None:
    """Create database tables if they don't exist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calls (
                call_id TEXT PRIMARY KEY,
                bank_name TEXT NOT NULL,
                quarter TEXT NOT NULL,
                source_url TEXT,
                source_type TEXT,
                processed_at TIMESTAMP,
                status TEXT,
                error_message TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to initialize database: {e}")

def register_call(
    call_id: str,
    bank: str,
    quarter: str,
    source_url: str,
    source_type: str,
    status: str = "success",
    error_message: Optional[str] = None
) -> None:
    """Register a call in the database with status tracking"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            INSERT OR REPLACE INTO calls 
            (call_id, bank_name, quarter, source_url, source_type, 
             processed_at, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            call_id,
            bank,
            quarter,
            source_url,
            source_type,
            datetime.now(),
            status,
            error_message
        ))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to register call: {e}")

@retry(FetchError, tries=MAX_RETRIES, delay=RETRY_DELAY)
def fetch_asset(url: str, output_path: Path) -> None:
    """Download an asset with retry logic"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(response.content)
        logging.info(f"Successfully downloaded {url} to {output_path}")
    except requests.RequestException as e:
        raise FetchError(f"Failed to fetch {url}: {e}")

def fetch_assets(bank: str, quarter: str) -> List[Path]:
    """
    Discover and download assets for a given bank + quarter.
    Returns a list of local file paths.
    """
    validate_bank_name(bank)
    validate_quarter(quarter)
    
    assets: List[Path] = []
    base_dir = RAW_DIR / bank / quarter
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Example: fetch from a bank's IR page (implement actual logic)
    # This is a placeholder - implement actual discovery logic
    urls = [
        f"https://example.com/{bank}/earnings/{quarter}/transcript.pdf",
        f"https://example.com/{bank}/earnings/{quarter}/presentation.pptx"
    ]
    
    for url in urls:
        try:
            # Extract filename from URL
            filename = os.path.basename(urlparse(url).path)
            output_path = base_dir / filename
            
            if not output_path.exists():
                fetch_asset(url, output_path)
                
            assets.append(output_path)
            
        except FetchError as e:
            logging.error(f"Failed to fetch {url}: {e}")
            continue
    
    return assets

def parse_pdf(path: Path) -> List[Dict[str, str]]:
    """
    Parse a PDF transcript or presentation.
    Returns a list of dicts: {speaker, timestamp, text}
    """
    try:
        records = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                    
                # Split text into speaker blocks
                blocks = text.split('\n\n')
                for block in blocks:
                    # Simple speaker detection (improve as needed)
                    if ':' in block:
                        speaker, content = block.split(':', 1)
                        records.append({
                            'speaker': speaker.strip(),
                            'timestamp': datetime.now().isoformat(),  # Add actual timestamp parsing
                            'text': content.strip()
                        })
        return records
    except Exception as e:
        raise ParseError(f"Failed to parse PDF {path}: {e}")

def parse_html(path: Path) -> List[Dict[str, str]]:
    """
    Parse an HTML transcript.
    Returns a list of dicts: {speaker, timestamp, text}
    """
    try:
        records = []
        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
            # Find all speaker blocks (implement actual HTML structure)
            blocks = soup.find_all('div', class_='speaker-block')
            for block in blocks:
                speaker = block.find('span', class_='speaker-name')
                timestamp = block.find('span', class_='timestamp')
                content = block.find('div', class_='content')
                
                if speaker and content:
                    records.append({
                        'speaker': speaker.text.strip(),
                        'timestamp': timestamp.text.strip() if timestamp else datetime.now().isoformat(),
                        'text': content.text.strip()
                    })
        return records
    except Exception as e:
        raise ParseError(f"Failed to parse HTML {path}: {e}")

def parse_vtt(path: Path) -> List[Dict[str, str]]:
    """
    Parse a VTT caption file.
    Returns a list of dicts: {speaker, timestamp, text}
    """
    try:
        records = []
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            current_timestamp = None
            current_text = []
            
            for line in lines:
                line = line.strip()
                if '-->' in line:  # Timestamp line
                    if current_timestamp and current_text:
                        records.append({
                            'speaker': 'UNKNOWN',  # Speaker detection needed
                            'timestamp': current_timestamp,
                            'text': ' '.join(current_text)
                        })
                    current_timestamp = line.split('-->')[0].strip()
                    current_text = []
                elif line and not line.isdigit():
                    current_text.append(line)
            
            if current_timestamp and current_text:
                records.append({
                    'speaker': 'UNKNOWN',
                    'timestamp': current_timestamp,
                    'text': ' '.join(current_text)
                })
        return records
    except Exception as e:
        raise ParseError(f"Failed to parse VTT {path}: {e}")

def clean_text(text: str) -> str:
    """Basic text cleaning function"""
    # Remove common fillers and normalize whitespace
    fillers = ['um', 'uh', 'ah', 'like', 'you know']
    text = text.lower()
    for filler in fillers:
        text = text.replace(filler, '')
    return ' '.join(text.split())

def normalize_speaker(speaker: str) -> str:
    """Normalize speaker names"""
    return speaker.strip().upper()

def clean_and_split(records: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Clean raw records and split into sentence-level entries.
    Input: list of {speaker, timestamp, text}
    Output: list of {speaker_norm, timestamp_epoch, timestamp_iso, sentence_id, text}
    """
    cleaned = []
    sentence_id = 0
    
    for record in records:
        try:
            # Clean and normalize text
            text = clean_text(record['text'])
            if not text:
                continue
                
            # Split into sentences
            sentences = sent_tokenize(text)
            
            # Create timestamp objects
            timestamp_iso = record['timestamp']
            timestamp_epoch = int(time.mktime(time.strptime(timestamp_iso, '%Y-%m-%dT%H:%M:%S')))
            
            # Normalize speaker
            speaker = normalize_speaker(record['speaker'])
            
            # Create sentence-level records
            for sentence in sentences:
                if sentence.strip():
                    cleaned.append({
                        'speaker_norm': speaker,
                        'timestamp_epoch': timestamp_epoch,
                        'timestamp_iso': timestamp_iso,
                        'sentence_id': f"{record['timestamp']}_{sentence_id}",
                        'text': sentence.strip()
                    })
                    sentence_id += 1
        except Exception as e:
            logging.error(f"Failed to clean record: {e}")
            continue
    
    return cleaned

def write_parquet(
    bank: str,
    quarter: str,
    call_id: str,
    records: List[Dict[str, str]]
) -> Path:
    """
    Write cleaned records to Parquet with proper schema.
    Returns the output file path.
    """
    try:
        out_dir = CLEAN_DIR / f"{bank}={quarter}"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame(records)
        
        # Define schema
        schema = pa.schema([
            ('speaker_norm', pa.string()),
            ('timestamp_epoch', pa.int64()),
            ('timestamp_iso', pa.string()),
            ('sentence_id', pa.string()),
            ('text', pa.string()),
            ('bank', pa.string()),
            ('quarter', pa.string()),
            ('call_id', pa.string())
        ])
        
        # Add metadata columns
        df['bank'] = bank
        df['quarter'] = quarter
        df['call_id'] = call_id
        
        # Convert to Arrow table with schema
        table = pa.Table.from_pandas(df, schema=schema)
        
        out_path = out_dir / f"{call_id}.parquet"
        
        # Write with schema
        with pa.OSFile(str(out_path), 'wb') as sink:
            with pa.RecordBatchFileWriter(sink, schema) as writer:
                writer.write_table(table)
        
        logging.info(f"Wrote {len(records)} records to {out_path}")
        return out_path
    except Exception as e:
        raise ETLException(f"Failed to write Parquet: {e}")

def process_call(bank: str, quarter: str) -> None:
    """
    Full pipeline for one bank + quarter:
    - fetch assets
    - for each asset, parse -> clean -> write -> register
    """
    try:
        validate_bank_name(bank)
        validate_quarter(quarter)
        
        logging.info(f"Starting processing for {bank} {quarter}")
        
        assets = fetch_assets(bank, quarter)
        if not assets:
            logging.warning(f"No assets found for {bank} {quarter}")
            return
            
        for asset_path in assets:
            try:
                source_type = asset_path.suffix.lstrip(".").upper()
                call_id = f"{bank}_{quarter}_{asset_path.stem}"
                
                # Parse based on file type
                if source_type == "PDF":
                    raw = parse_pdf(asset_path)
                elif source_type in ("HTML", "HTM"):
                    raw = parse_html(asset_path)
                elif source_type == "VTT":
                    raw = parse_vtt(asset_path)
                else:
                    logging.warning(f"Unsupported file type: {asset_path}")
                    continue
                
                if not raw:
                    logging.warning(f"No records parsed from {asset_path}")
                    continue
                    
                # Clean and split into sentences
                cleaned = clean_and_split(raw)
                if not cleaned:
                    logging.warning(f"No cleaned records for {asset_path}")
                    continue
                
                # Write to Parquet
                parquet_path = write_parquet(bank, quarter, call_id, cleaned)
                
                # Register in database
                register_call(call_id, bank, quarter, str(asset_path), source_type)
                
                logging.info(f"Successfully processed {asset_path}")
                
            except Exception as e:
                logging.error(f"Error processing {asset_path}: {e}")
                register_call(
                    call_id,
                    bank,
                    quarter,
                    str(asset_path),
                    source_type,
                    "error",
                    str(e)
                )
                continue
                
    except Exception as e:
        logging.error(f"Error processing {bank} {quarter}: {e}")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ETL for bank earnings calls")
    parser.add_argument(
        "--banks",
        nargs="+",
        help="List of bank names to process",
        required=True,
        type=str
    )
    parser.add_argument(
        "--quarters",
        nargs="+",
        help="List of quarters (e.g. Q1_2023) to process",
        required=True,
        type=str
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - don't write any files"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize database
        initialize_database()
        
        # Process each bank and quarter
        for bank in args.banks:
            for quarter in args.quarters:
                try:
                    if not args.dry_run:
                        process_call(bank, quarter)
                    else:
                        logging.info(f"Dry run: Would process {bank} {quarter}")
                except Exception as e:
                    logging.error(f"Failed to process {bank} {quarter}: {e}")
                    continue
                    
    except Exception as e:
        logging.error(f"ETL pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
