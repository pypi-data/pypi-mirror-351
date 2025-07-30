"""Google Sheets integration for reading email addresses."""

import os
from typing import List, Optional
from googleapiclient.discovery import build
from google.oauth2 import service_account


class GoogleSheetsReader:
    """Class for reading email addresses from Google Sheets."""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self, credentials_file: str = 'credentials.json'):
        """
        Initialize the Google Sheets reader.
        
        Args:
            credentials_file: Path to the Google service account credentials file.
        """
        self.credentials_file = credentials_file
        self.service = None
        self._setup_auth()
    
    def _setup_auth(self) -> bool:
        """Set up Google Sheets API authentication."""
        try:
            if not os.path.exists(self.credentials_file):
                print(f"Error: Google credentials file '{self.credentials_file}' not found.")
                print("Please download your credentials.json file from Google Cloud Console.")
                return False
            
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file, scopes=self.SCOPES
            )
            
            self.service = build('sheets', 'v4', credentials=creds)
            return True
            
        except Exception as e:
            print(f"Error setting up Google Sheets authentication: {e}")
            return False
    
    def read_emails(self, spreadsheet_id: str, range_name: str) -> List[str]:
        """
        Read email addresses from a Google Spreadsheet.
        
        Args:
            spreadsheet_id: The Google Spreadsheet ID.
            range_name: The range to read (e.g., 'Sheet1!B:B').
            
        Returns:
            List of unique email addresses.
        """
        try:
            if not self.service:
                print("Google Sheets service not available. Check authentication.")
                return []
            
            sheet = self.service.spreadsheets()
            
            # Get the values from the sheet
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
            
            if not values:
                print("No data found in the spreadsheet.")
                return []
            
            # Extract emails (assuming first row might be header)
            emails = []
            for i, row in enumerate(values):
                if row and len(row) > 0 and row[0]:
                    email = row[0].strip()
                    
                    # Skip header row if it doesn't look like an email
                    if i == 0 and '@' not in email:
                        continue
                        
                    # Basic email validation
                    if email and '@' in email and '.' in email:
                        emails.append(email.lower())  # Normalize to lowercase
            
            # Remove duplicates while preserving order
            seen = set()
            unique_emails = []
            for email in emails:
                if email not in seen:
                    seen.add(email)
                    unique_emails.append(email)
            
            print(f"Found {len(unique_emails)} unique email addresses in spreadsheet")
            return unique_emails
        
        except Exception as e:
            print(f"Error reading from Google Sheets: {e}")
            return []
    
    def validate_access(self, spreadsheet_id: str) -> bool:
        """
        Validate that we have access to the spreadsheet.
        
        Args:
            spreadsheet_id: The Google Spreadsheet ID to test.
            
        Returns:
            True if access is successful, False otherwise.
        """
        try:
            if not self.service:
                return False
            
            # Try to get spreadsheet metadata
            sheet = self.service.spreadsheets()
            result = sheet.get(spreadsheetId=spreadsheet_id).execute()
            
            title = result.get('properties', {}).get('title', 'Unknown')
            print(f"Successfully accessed spreadsheet: {title}")
            return True
            
        except Exception as e:
            print(f"Error accessing spreadsheet: {e}")
            print("Make sure:")
            print("1. The spreadsheet ID is correct")
            print("2. The service account has access to the spreadsheet")
            print("3. The credentials file is valid")
            return False 