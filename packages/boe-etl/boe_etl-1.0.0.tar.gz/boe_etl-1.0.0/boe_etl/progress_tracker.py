import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json
from .error_handling import get_exception_handler
from .config import ConfigManager

class ProgressTracker:
    """Progress tracking for ETL pipeline"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.progress_path = Path(self.config["logging"]["file"]).parent / "progress"
        self.progress_path.mkdir(parents=True, exist_ok=True)
        self.bank_progress = {}
        
    def start_bank_processing(self, bank_name: str, quarter: str) -> None:
        """
        Start tracking progress for a bank
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
        """
        key = f"{bank_name}_{quarter}"
        self.bank_progress[key] = {
            "start_time": datetime.now().isoformat(),
            "status": "processing",
            "stages": {
                "load": {"status": "pending", "count": 0},
                "clean": {"status": "pending", "count": 0},
                "topic": {"status": "pending", "count": 0},
                "store": {"status": "pending", "count": 0}
            },
            "errors": 0
        }
        
        self._save_progress()
        
    def update_stage_progress(
        self,
        bank_name: str,
        quarter: str,
        stage: str,
        count: int,
        status: str = "completed"
    ) -> None:
        """
        Update progress for a specific stage
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
            stage: Pipeline stage
            count: Number of records processed
            status: Stage status (completed/failed)
        """
        key = f"{bank_name}_{quarter}"
        if key not in self.bank_progress:
            self.start_bank_processing(bank_name, quarter)
            
        self.bank_progress[key]["stages"][stage] = {
            "status": status,
            "count": count
        }
        
        if status == "failed":
            self.bank_progress[key]["errors"] += 1
            
        self._save_progress()
        
    def complete_bank_processing(
        self,
        bank_name: str,
        quarter: str,
        success: bool = True
    ) -> None:
        """
        Mark bank processing as completed
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
            success: Whether processing was successful
        """
        key = f"{bank_name}_{quarter}"
        if key in self.bank_progress:
            self.bank_progress[key]["status"] = "success" if success else "failed"
            self.bank_progress[key]["end_time"] = datetime.now().isoformat()
            self._save_progress()
            
    def get_progress(self, bank_name: str, quarter: str) -> Dict:
        """
        Get progress for a specific bank
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
        Returns:
            Dictionary containing progress information
        """
        key = f"{bank_name}_{quarter}"
        return self.bank_progress.get(key, {
            "status": "not_started",
            "stages": {
                "load": {"status": "pending", "count": 0},
                "clean": {"status": "pending", "count": 0},
                "topic": {"status": "pending", "count": 0},
                "store": {"status": "pending", "count": 0}
            },
            "errors": 0
        })
    
    def get_all_progress(self) -> Dict:
        """Get progress for all banks"""
        return self.bank_progress
    
    def _save_progress(self) -> None:
        """Save progress to file"""
        progress_file = self.progress_path / "pipeline_progress.json"
        try:
            with open(progress_file, 'w') as f:
                json.dump(self.bank_progress, f, indent=2)
        except Exception as e:
            get_exception_handler().handle_error(
                e,
                "system",
                "progress_tracking",
                "save_progress"
            )

def get_progress_tracker() -> ProgressTracker:
    """Get the singleton progress tracker instance"""
    if not hasattr(get_progress_tracker, 'instance'):
        get_progress_tracker.instance = ProgressTracker()
    return get_progress_tracker.instance
