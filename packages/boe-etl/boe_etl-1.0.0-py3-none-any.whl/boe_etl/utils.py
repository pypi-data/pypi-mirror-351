import os
from pathlib import Path

def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent

def get_data_dir() -> Path:
    """Get the data directory"""
    return get_project_root() / "data"

def get_raw_data_dir() -> Path:
    """Get the raw data directory"""
    return get_data_dir() / "raw"

def get_processed_data_dir() -> Path:
    """Get the processed data directory"""
    return get_data_dir() / "processed"
