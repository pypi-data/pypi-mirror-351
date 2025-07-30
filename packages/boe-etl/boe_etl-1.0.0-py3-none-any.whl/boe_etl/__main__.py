"""Main entry point for the ETL pipeline.

This module initializes and runs the ETL pipeline with the specified configuration.
"""
import argparse
import logging
import sys
from pathlib import Path

from .etl_pipeline import ETLPipeline
from .config import ConfigManager, ConfigError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('etl_pipeline.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the ETL pipeline for bank earnings call data.')
    parser.add_argument(
        '--config', 
        type=str, 
        default='config/etl_config.yaml',
        help='Path to the configuration file (default: config/etl_config.yaml)'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    return parser.parse_args()

def setup_logging(level: str = 'INFO') -> None:
    """Configure logging with the specified level."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('etl_pipeline.log')
        ]
    )

def main():
    """Run the ETL pipeline with the specified configuration."""
    logger.info("=== Starting ETL Pipeline ===")
    logger.debug("Python path: %s", __import__('sys').path)
    
    try:
        # Parse command line arguments
        logger.debug("Parsing command line arguments")
        args = parse_args()
        
        # Set up logging
        logger.debug("Setting up logging with level: %s", args.log_level)
        setup_logging(args.log_level)
        
        # Initialize configuration
        config_path = Path(args.config).absolute()
        logger.info("Loading configuration from: %s", config_path)
        
        if not config_path.exists():
            error_msg = f"Configuration file not found at {config_path}"
            logger.critical(error_msg)
            raise ConfigError(error_msg)
        
        logger.debug("Initializing ConfigManager")
        config_manager = ConfigManager(config_path=config_path)
        
        logger.debug("Getting config from ConfigManager")
        config = config_manager.get_config()
        
        if not hasattr(config, 'banks') or not config.banks:
            logger.warning("No banks configured in the configuration file")
        else:
            logger.info("Loaded configuration for %d banks: %s", 
                       len(config.banks), 
                       [getattr(bank, 'name', 'unknown') for bank in config.banks])
        
        # Run the pipeline
        logger.info("Initializing ETLPipeline")
        pipeline = ETLPipeline(config=config)
        
        logger.info("Starting process_all_banks()")
        pipeline.process_all_banks()
        
        logger.info("=== ETL pipeline completed successfully ===")
        return 0
        
    except ConfigError as e:
        logger.error("=== Configuration error: %s ===", str(e), exc_info=True)
        return 1
    except ImportError as e:
        logger.critical("=== Import error: %s ===", str(e), exc_info=True)
        logger.critical("Python path: %s", __import__('sys').path)
        return 1
    except Exception as e:
        logger.critical("=== Unexpected error in ETL pipeline: %s ===", str(e), exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
