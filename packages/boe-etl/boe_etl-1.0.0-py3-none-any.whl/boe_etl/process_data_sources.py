"""Script to process data from the data_sources directory."""
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

class DataSourceProcessor:
    """Processes data from the data_sources directory."""
    
    def __init__(self, data_sources_dir: str, output_dir: str):
        """Initialize the data source processor.
        
        Args:
            data_sources_dir: Path to the data_sources directory
            output_dir: Path to the output directory
        """
        self.data_sources_dir = Path(data_sources_dir)
        self.output_dir = Path(output_dir)
        
        # Create output directories if they don't exist
        self.raw_dir = self.output_dir / 'raw'
        self.processed_dir = self.output_dir / 'processed'
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def get_quarter_dirs(self) -> List[Path]:
        """Get a list of quarter directories in the data_sources directory."""
        return [d for d in self.data_sources_dir.iterdir() if d.is_dir()]
    
    def process_quarter_dir(self, quarter_dir: Path) -> None:
        """Process a single quarter directory.
        
        Args:
            quarter_dir: Path to the quarter directory
        """
        quarter_name = quarter_dir.name
        logger.info(f"Processing quarter: {quarter_name}")
        
        # Create output directory for this quarter
        output_quarter_dir = self.raw_dir / quarter_name.replace(' ', '_')
        output_quarter_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each file in the quarter directory
        for file_path in quarter_dir.iterdir():
            if file_path.is_file():
                self._process_file(file_path, output_quarter_dir)
    
    def _process_file(self, file_path: Path, output_dir: Path) -> None:
        """Process a single file.
        
        Args:
            file_path: Path to the file to process
            output_dir: Directory to save the processed file
        """
        # Determine file type based on name
        file_name = file_path.name.lower()
        
        if 'transcript' in file_name:
            file_type = 'transcript'
        elif 'presentation' in file_name or 'prqtr' in file_name:
            file_type = 'presentation'
        elif 'supplement' in file_name or 'fsqtr' in file_name:
            file_type = 'supplement'
        elif 'rslt.xlsx' in file_name:
            file_type = 'results_excel'
        else:
            file_type = 'other'
        
        # Create output filename
        output_filename = f"{file_type}{file_path.suffix}"
        output_path = output_dir / output_filename
        
        # Copy the file to the output directory
        shutil.copy2(file_path, output_path)
        logger.info(f"Copied {file_path.name} to {output_path}")
    
    def run(self) -> None:
        """Run the data source processor."""
        logger.info(f"Starting data source processing from {self.data_sources_dir}")
        
        # Process each quarter directory
        for quarter_dir in self.get_quarter_dirs():
            self.process_quarter_dir(quarter_dir)
        
        logger.info(f"Finished processing data sources. Output saved to {self.output_dir}")

if __name__ == "__main__":
    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    data_sources_dir = project_root / 'data_sources'
    output_dir = project_root / 'data'
    
    # Run the processor
    processor = DataSourceProcessor(data_sources_dir, output_dir)
    processor.run()
