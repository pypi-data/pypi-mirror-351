"""Continuous monitoring module for Constant Contact Sheets Unsubscriber."""

import time
import argparse
import sys
from datetime import datetime
from typing import Optional

from .config import Config
from .core import ConstantContactUnsubscriber
from .sheets import GoogleSheetsReader


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser for monitoring."""
    parser = argparse.ArgumentParser(
        description='Continuously monitor Google Sheets for new emails to unsubscribe',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Start monitoring with default 5-minute intervals
  cc-monitor --spreadsheet-id "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" --range "Sheet1!B:B"
  
  # Monitor with custom interval (10 minutes)
  cc-monitor --spreadsheet-id "your_id" --range "Sheet1!B:B" --interval 600
  
  # Use custom credentials
  cc-monitor --spreadsheet-id "your_id" --range "Sheet1!B:B" --credentials my_creds.json
        '''
    )
    
    parser.add_argument(
        '--spreadsheet-id',
        required=True,
        help='Google Spreadsheet ID (found in the URL)'
    )
    
    parser.add_argument(
        '--range',
        required=True,
        help='Range to read emails from (e.g., "Sheet1!B:B")'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        help='Check interval in seconds (default from environment or 300)'
    )
    
    parser.add_argument(
        '--credentials',
        default='credentials.json',
        help='Path to Google service account credentials file (default: credentials.json)'
    )
    
    parser.add_argument(
        '--env-file',
        help='Path to .env file with API credentials'
    )
    
    parser.add_argument(
        '--max-failures',
        type=int,
        default=3,
        help='Maximum consecutive failures before stopping (default: 3)'
    )
    
    return parser


def run_single_check(unsubscriber: ConstantContactUnsubscriber, sheets_reader: GoogleSheetsReader,
                    spreadsheet_id: str, range_name: str) -> bool:
    """
    Run a single check for new emails.
    
    Args:
        unsubscriber: The ConstantContactUnsubscriber instance.
        sheets_reader: The GoogleSheetsReader instance.
        spreadsheet_id: Google Spreadsheet ID.
        range_name: Range to read emails from.
        
    Returns:
        True if successful, False if error occurred.
    """
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{timestamp}] 🔍 Checking for new emails...")
        
        # Read emails from spreadsheet
        emails = sheets_reader.read_emails(spreadsheet_id, range_name)
        
        if not emails:
            print("⚠️  No emails found in spreadsheet")
            return True
        
        # Process emails (not in initialize mode)
        result = unsubscriber.process_emails(emails, initialize_mode=False)
        
        if 'new_emails' in result and result['new_emails'] == 0:
            print("✅ No new emails to process")
        elif 'new_emails_processed' in result:
            print(f"📊 Processed {result['new_emails_processed']} new emails:")
            print(f"   ✅ Successfully unsubscribed: {result['success_count']}")
            print(f"   ❓ Not found: {result['not_found_count']}")
            print(f"   ❌ Errors: {result['error_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during check: {e}")
        return False


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the monitoring CLI.
    
    Args:
        args: Command line arguments (for testing)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    print("🔄 Constant Contact Google Sheets Monitor")
    print("=" * 50)
    
    try:
        # Initialize configuration
        config = Config(parsed_args.env_file)
        
        # Get check interval from args or config
        check_interval = parsed_args.interval or config.check_interval_seconds
        
        # Validate configuration
        if not config.validate():
            print("❌ Missing required configuration:")
            for var in config.get_missing_config():
                print(f"  - {var}")
            print("\nPlease set these environment variables in your .env file.")
            return 1
        
        # Initialize components
        print(f"📊 Setting up Google Sheets access...")
        sheets_reader = GoogleSheetsReader(parsed_args.credentials)
        
        if not sheets_reader.validate_access(parsed_args.spreadsheet_id):
            print("❌ Failed to access Google Spreadsheet")
            return 1
        
        print(f"🔧 Setting up Constant Contact API...")
        unsubscriber = ConstantContactUnsubscriber(config)
        
        # Display configuration
        print(f"\n📋 Monitoring Configuration:")
        print(f"   📊 Spreadsheet ID: {parsed_args.spreadsheet_id}")
        print(f"   📍 Range: {parsed_args.range}")
        print(f"   ⏰ Check interval: {check_interval} seconds ({check_interval//60} minutes)")
        print(f"   ⚠️  Max failures: {parsed_args.max_failures}")
        print(f"   📁 Processed emails file: {config.processed_emails_file}")
        print(f"   📝 Success log file: {config.success_log_file}")
        
        print(f"\n🚀 Starting continuous monitoring...")
        print(f"   Press Ctrl+C to stop\n")
        
        consecutive_failures = 0
        
        while True:
            success = run_single_check(
                unsubscriber, sheets_reader, 
                parsed_args.spreadsheet_id, parsed_args.range
            )
            
            if success:
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                print(f"⚠️  Consecutive failures: {consecutive_failures}/{parsed_args.max_failures}")
                
                if consecutive_failures >= parsed_args.max_failures:
                    print(f"\n💥 Too many consecutive failures ({parsed_args.max_failures})")
                    print("🛑 Stopping monitoring to prevent further issues")
                    return 1
            
            print(f"⏳ Waiting {check_interval} seconds before next check...")
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Monitoring stopped by user")
        print(f"✅ Graceful shutdown complete")
        return 0
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 