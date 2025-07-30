"""Command line interface for Constant Contact Sheets Unsubscriber."""

import argparse
import sys
from typing import Optional

from .config import Config
from .core import ConstantContactUnsubscriber
from .sheets import GoogleSheetsReader


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='Unsubscribe emails from Constant Contact using Google Sheets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Initialize - mark existing emails as processed
  cc-unsubscriber --spreadsheet-id "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" --range "Sheet1!B:B" --initialize
  
  # Process new emails
  cc-unsubscriber --spreadsheet-id "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" --range "Sheet1!B:B"
  
  # Use custom credentials file
  cc-unsubscriber --spreadsheet-id "your_id" --range "Sheet1!B:B" --credentials my_creds.json
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
        '--initialize',
        action='store_true',
        help='Mark all current emails as processed without unsubscribing (first run only)'
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
        '--validate-only',
        action='store_true',
        help='Only validate access to Google Sheets and Constant Contact, don\'t process emails'
    )
    
    return parser


def validate_configuration(config: Config) -> bool:
    """
    Validate that all required configuration is present.
    
    Args:
        config: Configuration object to validate.
        
    Returns:
        True if valid, False otherwise.
    """
    if not config.validate():
        print("❌ Missing required configuration:")
        for var in config.get_missing_config():
            print(f"  - {var}")
        print("\nPlease set these environment variables in your .env file.")
        print("See the documentation for setup instructions.")
        return False
    
    print("✅ Configuration validated successfully")
    return True


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command line arguments (for testing)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    print("🚀 Constant Contact Google Sheets Unsubscriber")
    print("=" * 50)
    
    try:
        # Initialize configuration
        config = Config(parsed_args.env_file)
        
        # Validate configuration (skip for initialize-only runs)
        if not parsed_args.validate_only and not parsed_args.initialize:
            if not validate_configuration(config):
                return 1
        
        # Initialize Google Sheets reader
        print(f"📊 Setting up Google Sheets access...")
        sheets_reader = GoogleSheetsReader(parsed_args.credentials)
        
        # Validate Google Sheets access
        if not sheets_reader.validate_access(parsed_args.spreadsheet_id):
            print("❌ Failed to access Google Spreadsheet")
            return 1
        
        if parsed_args.validate_only:
            print("✅ Validation complete - all systems accessible")
            return 0
        
        # Read emails from spreadsheet
        print(f"📖 Reading emails from range: {parsed_args.range}")
        emails = sheets_reader.read_emails(parsed_args.spreadsheet_id, parsed_args.range)
        
        if not emails:
            print("⚠️  No emails found in the specified range")
            return 0
        
        # Initialize Constant Contact unsubscriber
        print(f"🔧 Setting up Constant Contact API...")
        unsubscriber = ConstantContactUnsubscriber(config)
        
        # Process emails
        if parsed_args.initialize:
            print(f"🔄 INITIALIZATION MODE")
            print(f"   Marking {len(emails)} emails as already processed...")
        else:
            print(f"📧 Processing {len(emails)} total emails...")
        
        result = unsubscriber.process_emails(emails, parsed_args.initialize)
        
        # Print results
        if parsed_args.initialize:
            print(f"\n✅ Initialization Complete!")
            print(f"   📝 {result['initialized']} emails marked as processed")
            print(f"   🚀 Future runs will only process NEW emails")
        else:
            if result['new_emails'] == 0:
                print(f"\n✅ No new emails to process")
                print(f"   All emails have been handled previously")
            else:
                print(f"\n📊 Processing Results:")
                print(f"   🆕 New emails processed: {result['new_emails_processed']}")
                print(f"   ✅ Successfully unsubscribed: {result['success_count']}")
                print(f"   ❓ Contacts not found: {result['not_found_count']}")
                print(f"   ❌ Errors: {result['error_count']}")
                print(f"   📈 Total processed (all time): {result['total_processed']}")
                
                if result['not_found_emails']:
                    print(f"\n📝 Emails not found in Constant Contact:")
                    for email in result['not_found_emails'][:5]:  # Show first 5
                        print(f"     - {email}")
                    if len(result['not_found_emails']) > 5:
                        print(f"     ... and {len(result['not_found_emails']) - 5} more")
        
        print(f"\n🎉 Operation completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n🛑 Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 