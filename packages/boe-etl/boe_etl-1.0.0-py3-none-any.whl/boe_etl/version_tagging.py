import json
from typing import Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime
from .data_versioning import get_data_version_manager
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

class VersionTagManager:
    """Manager for version tags and labels"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.version_manager = get_data_version_manager()
        self.tags_path = self.version_manager.versions_path / "tags"
        self._create_tag_directories()
    
    def _create_tag_directories(self):
        """Create tag management directories"""
        self.tags_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created tag management directory: {self.tags_path}")
    
    def create_tag(self, tag_name: str, bank_name: str, quarter: str, version_id: str, description: str = ""):
        """
        Create a tag for a specific version
        Args:
            tag_name: Name of the tag (e.g., "production", "baseline")
            bank_name: Name of the bank
            quarter: Quarter identifier
            version_id: Version ID to tag
            description: Optional description of the tag
        """
        if not self.version_manager._is_valid_version(
            self.version_manager._get_version_path(bank_name, quarter, version_id)
        ):
            raise ValueError(f"Version {version_id} does not exist")
        
        tag_file = self.tags_path / f"{bank_name}_{quarter}_{tag_name}.json"
        
        # Create or update tag file
        if tag_file.exists():
            with open(tag_file, 'r') as f:
                tags = json.load(f)
        else:
            tags = {}
        
        tags[version_id] = {
            "created_at": datetime.now().isoformat(),
            "description": description,
            "bank_name": bank_name,
            "quarter": quarter
        }
        
        with open(tag_file, 'w') as f:
            json.dump(tags, f, indent=2)
        
        logging.info(f"Created tag {tag_name} for version {version_id}")
    
    def get_tagged_versions(self, tag_name: str, bank_name: str, quarter: str) -> Dict[str, Dict]:
        """
        Get all versions tagged with a specific tag
        Args:
            tag_name: Name of the tag
            bank_name: Name of the bank
            quarter: Quarter identifier
        Returns:
            Dictionary mapping version IDs to tag metadata
        """
        tag_file = self.tags_path / f"{bank_name}_{quarter}_{tag_name}.json"
        if not tag_file.exists():
            return {}
            
        with open(tag_file, 'r') as f:
            return json.load(f)
    
    def remove_tag(self, tag_name: str, bank_name: str, quarter: str, version_id: str) -> bool:
        """
        Remove a tag from a version
        Args:
            tag_name: Name of the tag
            bank_name: Name of the bank
            quarter: Quarter identifier
            version_id: Version ID to remove tag from
        Returns:
            True if successful, False otherwise
        """
        try:
            tag_file = self.tags_path / f"{bank_name}_{quarter}_{tag_name}.json"
            if not tag_file.exists():
                return False
                
            with open(tag_file, 'r') as f:
                tags = json.load(f)
                
            if version_id not in tags:
                return False
                
            del tags[version_id]
            
            if tags:  # If there are still other versions with this tag
                with open(tag_file, 'w') as f:
                    json.dump(tags, f, indent=2)
            else:  # If this was the last version with this tag
                tag_file.unlink()
                
            logging.info(f"Removed tag {tag_name} from version {version_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to remove tag {tag_name} from version {version_id}: {e}")
            return False
    
    def list_tags(self, bank_name: str, quarter: str) -> Dict[str, List[str]]:
        """
        List all tags for a bank and quarter
        Returns:
            Dictionary mapping tag names to version IDs
        """
        tags = {}
        for tag_file in self.tags_path.glob(f"{bank_name}_{quarter}_*.json"):
            tag_name = tag_file.stem.split('_')[-1]
            with open(tag_file, 'r') as f:
                versions = list(json.load(f).keys())
            tags[tag_name] = versions
        return tags
    
    def get_latest_tagged_version(self, tag_name: str, bank_name: str, quarter: str) -> Optional[str]:
        """
        Get the latest version with a specific tag
        Args:
            tag_name: Name of the tag
            bank_name: Name of the bank
            quarter: Quarter identifier
        Returns:
            Latest version ID with the tag, or None if no versions are tagged
        """
        versions = self.get_tagged_versions(tag_name, bank_name, quarter)
        if not versions:
            return None
            
        return max(versions.keys(), key=lambda k: versions[k]["created_at"])

def get_version_tag_manager() -> VersionTagManager:
    """Get the singleton version tag manager instance"""
    if not hasattr(get_version_tag_manager, 'instance'):
        get_version_tag_manager.instance = VersionTagManager()
    return get_version_tag_manager.instance
