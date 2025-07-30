"""Utility functions for the Constant Contact Sheets Unsubscriber package."""

from typing import Dict, Any
from .config import Config
from .core import ConstantContactUnsubscriber
from .sheets import GoogleSheetsReader


def process_sheet(spreadsheet_id: str, range_name: str, 
                 initialize_mode: bool = False, 
                 config: Config = None,
                 credentials_file: str = 'credentials.json') -> Dict[str, Any]:
    """
    High-level function to process a Google Sheet for unsubscribes.
    
    Args:
        spreadsheet_id: Google Spreadsheet ID.
        range_name: Range to read emails from (e.g., 'Sheet1!B:B').
        initialize_mode: If True, mark emails as processed without unsubscribing.
        config: Configuration object. If None, creates default.
        credentials_file: Path to Google credentials file.
        
    Returns:
        Dictionary with processing results.
    """
    # Initialize config if not provided
    if config is None:
        config = Config()
    
    # Initialize Google Sheets reader
    sheets_reader = GoogleSheetsReader(credentials_file)
    
    # Validate access
    if not sheets_reader.validate_access(spreadsheet_id):
        return {'error': 'Failed to access Google Spreadsheet'}
    
    # Read emails
    emails = sheets_reader.read_emails(spreadsheet_id, range_name)
    
    if not emails:
        return {'error': 'No emails found in spreadsheet'}
    
    # Initialize unsubscriber
    unsubscriber = ConstantContactUnsubscriber(config)
    
    # Process emails
    return unsubscriber.process_emails(emails, initialize_mode)


def validate_setup(spreadsheet_id: str = None, 
                  credentials_file: str = 'credentials.json',
                  config: Config = None) -> Dict[str, bool]:
    """
    Validate the complete setup including Google Sheets and Constant Contact access.
    
    Args:
        spreadsheet_id: Google Spreadsheet ID to test (optional).
        credentials_file: Path to Google credentials file.
        config: Configuration object. If None, creates default.
        
    Returns:
        Dictionary with validation results.
    """
    results = {
        'config_valid': False,
        'google_sheets_auth': False,
        'google_sheets_access': False,
        'constant_contact_valid': False
    }
    
    try:
        # Check configuration
        if config is None:
            config = Config()
        
        results['config_valid'] = config.validate()
        
        # Check Google Sheets authentication
        sheets_reader = GoogleSheetsReader(credentials_file)
        results['google_sheets_auth'] = sheets_reader.service is not None
        
        # Check Google Sheets access (if spreadsheet ID provided)
        if spreadsheet_id and results['google_sheets_auth']:
            results['google_sheets_access'] = sheets_reader.validate_access(spreadsheet_id)
        
        # Check Constant Contact (if config is valid)
        if results['config_valid']:
            try:
                unsubscriber = ConstantContactUnsubscriber(config)
                # Try to refresh token as a validation
                results['constant_contact_valid'] = unsubscriber.refresh_access_token()
            except Exception:
                results['constant_contact_valid'] = False
        
    except Exception as e:
        print(f"Validation error: {e}")
    
    return results


def get_status_summary(config: Config = None) -> Dict[str, Any]:
    """
    Get a summary of the current status including processed emails count.
    
    Args:
        config: Configuration object. If None, creates default.
        
    Returns:
        Dictionary with status information.
    """
    if config is None:
        config = Config()
    
    try:
        unsubscriber = ConstantContactUnsubscriber(config)
        processed_emails = unsubscriber.load_processed_emails()
        
        return {
            'total_processed_emails': len(processed_emails),
            'processed_emails_file': config.processed_emails_file,
            'success_log_file': config.success_log_file,
            'rate_limit_seconds': config.rate_limit_seconds,
            'check_interval_seconds': config.check_interval_seconds
        }
    except Exception as e:
        return {'error': str(e)} 