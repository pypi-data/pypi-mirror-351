import os
from pathlib import Path
import shutil
from datetime import datetime
import logging
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from etl.config import ConfigManager
from etl.utils import get_project_root

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

class DataStandardizer:
    """Class for standardizing data source files"""
    def __init__(self, source_dir: Path, target_dir: Path):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.config = ConfigManager().get_config()
        
    def standardize_quarter_name(self, quarter: str) -> str:
        """Standardize quarter directory names"""
        # Convert to format QX_YYYY
        if len(quarter) == 7:  # Format: QX YYYY
            return f"Q{quarter[1]}_{quarter[3:7]}"
        elif len(quarter) == 6:  # Format: QX_YYYY
            return quarter
        else:
            raise ValueError(f"Invalid quarter format: {quarter}")
    
    def standardize_file_name(self, file_path: Path, quarter: str) -> str:
        """Standardize file names"""
        quarter_code = quarter.replace("_", "")
        
        # Extract file type from extension
        ext = file_path.suffix.lower()
        if ext == '.pdf':
            if 'transcript' in file_path.stem.lower():
                return f"transcript_{quarter_code}{ext}"
            elif 'presentation' in file_path.stem.lower():
                return f"presentation_{quarter_code}{ext}"
            elif 'financial' in file_path.stem.lower():
                return f"financial_{quarter_code}{ext}"
            else:
                return f"document_{quarter_code}{ext}"
        elif ext == '.xlsx':
            return f"financial_{quarter_code}{ext}"
        else:
            return f"{file_path.stem}_{quarter_code}{ext}"
    
    def standardize_directory(self, quarter_dir: Path) -> None:
        """Standardize files in a quarter directory"""
        try:
            quarter = quarter_dir.name
            standardized_quarter = self.standardize_quarter_name(quarter)
            
            # Create target directory
            target_quarter_dir = self.target_dir / standardized_quarter
            target_quarter_dir.mkdir(parents=True, exist_ok=True)
            
            # Process each file
            for file_path in quarter_dir.glob("*"):
                if file_path.is_file():
                    try:
                        # Standardize filename
                        new_name = self.standardize_file_name(file_path, standardized_quarter)
                        target_path = target_quarter_dir / new_name
                        
                        # Copy and rename file
                        shutil.copy2(file_path, target_path)
                        logging.info(f"Standardized {file_path} -> {target_path}")
                        
                    except Exception as e:
                        logging.error(f"Failed to standardize {file_path}: {e}")
                        continue
            
        except Exception as e:
            logging.error(f"Failed to standardize quarter {quarter}: {e}")
    
    def standardize_all(self) -> None:
        """Standardize all files in source directory"""
        logging.info("Starting data standardization process")
        
        # Process each quarter directory
        for quarter_dir in self.source_dir.glob("*"):
            if quarter_dir.is_dir():
                self.standardize_directory(quarter_dir)
        
        logging.info("Data standardization completed")

def main():
    """Main function to run standardization"""
    source_dir = Path("data_sources")
    target_dir = Path("data") / "raw"
    
    # Create target directory structure
    target_dir.mkdir(parents=True, exist_ok=True)
    
    standardizer = DataStandardizer(source_dir, target_dir)
    standardizer.standardize_all()

if __name__ == "__main__":
    main()
