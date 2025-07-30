"""Version tag management for data versioning."""
from typing import Optional, Dict, Any
from pathlib import Path
import json
import logging
from datetime import datetime

class VersionTagManager:
    """Manages version tags for data versioning."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the version tag manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
    def get_version_tag(self) -> str:
        """Generate a version tag based on the current timestamp.
        
        Returns:
            str: Version tag in format 'YYYYMMDD_HHMMSS'
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def save_version_info(self, version_tag: str, metadata: Dict[str, Any], output_dir: Path) -> None:
        """Save version information to a JSON file.
        
        Args:
            version_tag: Version tag
            metadata: Additional metadata to save
            output_dir: Directory to save the version info file
        """
        version_info = {
            "version_tag": version_tag,
            "created_at": datetime.now().isoformat(),
            **metadata
        }
        
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"version_{version_tag}.json"
        
        with open(output_file, 'w') as f:
            json.dump(version_info, f, indent=2)
        
        self.logger.info(f"Saved version info to {output_file}")
    
    def create_tag(self, tag_name: str, bank_name: str, quarter: str, version_id: str, description: str) -> None:
        """Create a tag for a specific version.
        
        Args:
            tag_name: Name of the tag
            bank_name: Name of the bank
            quarter: Quarter identifier
            version_id: Version ID to tag
            description: Description of the tag
        """
        tag_info = {
            "tag_name": tag_name,
            "version_id": version_id,
            "bank_name": bank_name,
            "quarter": quarter,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        # Create tags directory in version folder
        version_dir = Path("data/metadata/versions") / bank_name / quarter / version_id
        tags_dir = version_dir / "tags"
        tags_dir.mkdir(parents=True, exist_ok=True)
        
        # Save tag file
        tag_file = tags_dir / f"{tag_name}.json"
        with open(tag_file, 'w') as f:
            json.dump(tag_info, f, indent=2)
        
        self.logger.info(f"Created tag '{tag_name}' for version {version_id}")

# Singleton instance
_version_tag_manager = None

def get_version_tag_manager() -> VersionTagManager:
    """Get the singleton instance of VersionTagManager.
    
    Returns:
        VersionTagManager: The singleton instance
    """
    global _version_tag_manager
    if _version_tag_manager is None:
        _version_tag_manager = VersionTagManager()
    return _version_tag_manager
