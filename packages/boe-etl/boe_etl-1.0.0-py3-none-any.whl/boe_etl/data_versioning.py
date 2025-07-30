import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Union, Any
from .storage_config import get_storage_config
from .config import ConfigManager
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

class DataVersionManager:
    """Data versioning manager for version control of processed data"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.storage = get_storage_config()
        self.versions_path = self.storage.metadata_path / "versions"
        self._create_version_directories()
    
    def _create_version_directories(self):
        """Create version management directories"""
        self.versions_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created version management directory: {self.versions_path}")
    
    def create_version(self, bank_name: str, quarter: str, version_info: Dict) -> str:
        """
        Create a new version of data
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
            version_info: Dictionary containing version metadata
        Returns:
            Version ID
        """
        version_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_dir = self._get_version_path(bank_name, quarter, version_id)
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Create version metadata
        version_metadata = {
            "version_id": version_id,
            "bank_name": bank_name,
            "quarter": quarter,
            "created_at": datetime.now().isoformat(),
            "version_info": version_info
        }
        
        metadata_file = version_dir / "version_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(version_metadata, f, indent=2)
        
        logging.info(f"Created new version {version_id} for {bank_name} {quarter}")
        return version_id
    
    def _get_version_path(self, bank_name: str, quarter: str, version_id: str) -> Path:
        """Get path for a specific version"""
        return self.versions_path / bank_name / quarter / version_id
    
    def get_latest_version(self, bank_name: str, quarter: str) -> Optional[str]:
        """Get the latest version ID for a bank and quarter"""
        version_dir = self.versions_path / bank_name / quarter
        if not version_dir.exists():
            return None
            
        versions = sorted([
            d.name for d in version_dir.iterdir() 
            if d.is_dir() and self._is_valid_version(d)
        ])
        
        return versions[-1] if versions else None
    
    def _is_valid_version(self, version_dir: Path) -> bool:
        """Check if a directory is a valid version directory"""
        return (version_dir / "version_metadata.json").exists()
    
    def rollback_to_version(self, bank_name: str, quarter: str, version_id: str) -> bool:
        """
        Rollback data to a specific version
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
            version_id: Version ID to rollback to
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get paths
            version_path = self._get_version_path(bank_name, quarter, version_id)
            current_path = self.storage.get_bank_data_path(bank_name, quarter)
            
            if not version_path.exists():
                raise ValueError(f"Version {version_id} does not exist")
            
            # Backup current data
            backup_path = self.storage.temp_path / f"backup_{version_id}"
            if current_path.exists():
                shutil.copytree(current_path, backup_path)
            
            # Restore version
            shutil.rmtree(current_path, ignore_errors=True)
            shutil.copytree(version_path, current_path)
            
            logging.info(f"Successfully rolled back to version {version_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to rollback to version {version_id}: {e}")
            return False
    
    def list_versions(self, bank_name: str, quarter: str) -> List[Dict]:
        """List all versions for a bank and quarter"""
        versions = []
        version_dir = self.versions_path / bank_name / quarter
        
        if not version_dir.exists():
            return versions
            
        for version_id in sorted([
            d.name for d in version_dir.iterdir() 
            if d.is_dir() and self._is_valid_version(d)
        ]):
            metadata_file = self._get_version_path(bank_name, quarter, version_id) / "version_metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                versions.append({
                    "version_id": version_id,
                    "created_at": metadata["created_at"],
                    "version_info": metadata["version_info"]
                })
        
        return versions
    
    def get_version_metadata(self, bank_name: str, quarter: str, version_id: str) -> Optional[Dict]:
        """Get metadata for a specific version"""
        metadata_file = self._get_version_path(bank_name, quarter, version_id) / "version_metadata.json"
        if not metadata_file.exists():
            return None
            
        with open(metadata_file, 'r') as f:
            return json.load(f)
    
    def compare_versions(self, bank_name: str, quarter: str, version1: str, version2: str) -> Dict:
        """
        Compare two versions of data
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
            version1: First version ID
            version2: Second version ID
        Returns:
            Dictionary containing comparison results
        """
        v1_path = self._get_version_path(bank_name, quarter, version1)
        v2_path = self._get_version_path(bank_name, quarter, version2)
        
        if not v1_path.exists() or not v2_path.exists():
            raise ValueError("One or both versions do not exist")
            
        # Get metadata
        v1_meta = self.get_version_metadata(bank_name, quarter, version1)
        v2_meta = self.get_version_metadata(bank_name, quarter, version2)
        
        # Compare metadata
        comparison = {
            "version1": version1,
            "version2": version2,
            "metadata_changes": self._compare_dictionaries(v1_meta, v2_meta)
        }
        
        return comparison
    
    def _compare_dictionaries(self, dict1: Dict, dict2: Dict) -> Dict:
        """Compare two dictionaries recursively"""
        changes = {}
        
        # Find keys that exist in both
        common_keys = set(dict1.keys()) & set(dict2.keys())
        for key in common_keys:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                changes[key] = self._compare_dictionaries(dict1[key], dict2[key])
            elif dict1[key] != dict2[key]:
                changes[key] = {
                    "old": dict1[key],
                    "new": dict2[key]
                }
        
        # Find keys that exist only in one
        for key in set(dict1.keys()) - set(dict2.keys()):
            changes[key] = {"old": dict1[key], "new": None}
        
        for key in set(dict2.keys()) - set(dict1.keys()):
            changes[key] = {"old": None, "new": dict2[key]}
        
        return changes

def get_data_version_manager() -> DataVersionManager:
    """Get the singleton data version manager instance"""
    if not hasattr(get_data_version_manager, 'instance'):
        get_data_version_manager.instance = DataVersionManager()
    return get_data_version_manager.instance
