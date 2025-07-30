#!/usr/bin/env python3
"""
BoE ETL Command Line Interface
==============================

Command line tools for the BoE ETL package.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .core import ETLPipeline
from .frontend import launch_frontend


def process_command(args):
    """Handle the process command."""
    pipeline = ETLPipeline()
    
    if args.file:
        # Process single file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 1
        
        print(f"🔄 Processing {file_path}...")
        results = pipeline.process_document(
            file_path, 
            args.institution, 
            args.quarter,
            include_nlp=not args.no_nlp
        )
        
        if results:
            output_path = args.output or f"{args.institution}_{args.quarter}_processed.csv"
            pipeline.save_results(results, output_path, format=args.format)
            print(f"✅ Processed {len(results)} records -> {output_path}")
        else:
            print("⚠️  No data extracted")
            return 1
    
    elif args.directory:
        # Process directory
        dir_path = Path(args.directory)
        if not dir_path.exists():
            print(f"❌ Directory not found: {dir_path}")
            return 1
        
        print(f"🔄 Processing directory {dir_path}...")
        results = pipeline.process_directory(
            dir_path,
            args.institution,
            args.quarter,
            include_nlp=not args.no_nlp,
            recursive=args.recursive
        )
        
        if results:
            output_path = args.output or f"{args.institution}_{args.quarter}_batch_processed.csv"
            pipeline.save_results(results, output_path, format=args.format)
            print(f"✅ Processed {len(results)} records from directory -> {output_path}")
        else:
            print("⚠️  No data extracted from directory")
            return 1
    
    else:
        print("❌ Must specify either --file or --directory")
        return 1
    
    return 0


def frontend_command(args):
    """Handle the frontend command."""
    print(f"🚀 Launching BoE ETL Frontend on port {args.port}...")
    try:
        launch_frontend(port=args.port, host=args.host)
    except KeyboardInterrupt:
        print("\n👋 Frontend stopped")
    except Exception as e:
        print(f"❌ Failed to launch frontend: {e}")
        return 1
    return 0


def validate_command(args):
    """Handle the validate command."""
    import pandas as pd
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return 1
    
    try:
        # Load the file
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() == '.parquet':
            df = pd.read_parquet(file_path)
        else:
            print(f"❌ Unsupported file format: {file_path.suffix}")
            return 1
        
        # Convert to records for validation
        records = df.to_dict('records')
        
        # Validate using pipeline
        pipeline = ETLPipeline()
        validation_report = pipeline.validate_results(records)
        
        print(f"📊 Validation Report for {file_path}")
        print("-" * 40)
        print(f"Valid: {'✅ Yes' if validation_report['valid'] else '❌ No'}")
        print(f"Records: {validation_report['record_count']:,}")
        print(f"Columns: {validation_report['column_count']}")
        
        if validation_report['errors']:
            print("\n❌ Errors found:")
            for error in validation_report['errors']:
                print(f"  • {error}")
        else:
            print("\n✅ No validation errors found")
        
        if args.verbose and 'columns' in validation_report:
            print(f"\n📋 Columns: {', '.join(validation_report['columns'])}")
        
        return 0 if validation_report['valid'] else 1
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="BoE ETL - Financial Document Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  boe-etl process --file earnings.pdf --institution JPMorgan --quarter Q1_2025
  boe-etl process --directory ./docs --institution Citigroup --quarter Q2_2025
  boe-etl frontend --port 8080
  boe-etl validate --file processed_data.csv
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process documents')
    process_group = process_parser.add_mutually_exclusive_group(required=True)
    process_group.add_argument('--file', '-f', help='Process a single file')
    process_group.add_argument('--directory', '-d', help='Process all files in directory')
    
    process_parser.add_argument('--institution', '-i', required=True, help='Institution name')
    process_parser.add_argument('--quarter', '-q', required=True, help='Quarter (e.g., Q1_2025)')
    process_parser.add_argument('--output', '-o', help='Output file path')
    process_parser.add_argument('--format', choices=['csv', 'parquet', 'json'], default='csv', help='Output format')
    process_parser.add_argument('--no-nlp', action='store_true', help='Skip NLP feature extraction')
    process_parser.add_argument('--recursive', '-r', action='store_true', help='Process subdirectories recursively')
    
    # Frontend command
    frontend_parser = subparsers.add_parser('frontend', help='Launch web frontend')
    frontend_parser.add_argument('--port', '-p', type=int, default=8501, help='Port number (default: 8501)')
    frontend_parser.add_argument('--host', default='localhost', help='Host address (default: localhost)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate processed data')
    validate_parser.add_argument('--file', '-f', required=True, help='File to validate')
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Handle commands
    if args.command == 'process':
        return process_command(args)
    elif args.command == 'frontend':
        return frontend_command(args)
    elif args.command == 'validate':
        return validate_command(args)
    elif args.command == 'version':
        from . import __version__, __author__
        print(f"BoE ETL version {__version__}")
        print(f"Author: {__author__}")
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())