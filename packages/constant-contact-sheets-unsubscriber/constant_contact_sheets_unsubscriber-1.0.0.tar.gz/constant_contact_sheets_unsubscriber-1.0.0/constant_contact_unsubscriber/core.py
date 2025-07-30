"""Core Constant Contact unsubscriber functionality."""

import os
import time
import json
import requests
from datetime import datetime
from typing import Optional, List, Set, Dict, Any
from .config import Config


class ConstantContactUnsubscriber:
    """Main class for handling Constant Contact unsubscribe operations."""
    
    # API endpoints
    BASE_URL = 'https://api.cc.email/v3'
    AUTH_URL = 'https://authz.constantcontact.com/oauth2/default/v1/token'
    
    def __init__(self, config: Config):
        """
        Initialize the unsubscriber.
        
        Args:
            config: Configuration object with API credentials.
        """
        self.config = config
        self.access_token = config.constant_contact_access_token
        self.refresh_token = config.constant_contact_refresh_token
        self.processed_emails_file = config.processed_emails_file
        self.success_log_file = config.success_log_file
    
    def process_sheet(self, spreadsheet_id: str, range_name: str, 
                     initialize_mode: bool = False) -> Dict[str, Any]:
        """
        Process emails from a Google Spreadsheet.
        
        Args:
            spreadsheet_id: Google Spreadsheet ID.
            range_name: Range to read emails from (e.g., 'Sheet1!B:B').
            initialize_mode: If True, mark emails as processed without unsubscribing.
            
        Returns:
            Dictionary with processing results.
        """
        from .sheets import GoogleSheetsReader
        
        # Initialize Google Sheets reader
        sheets_reader = GoogleSheetsReader(self.config.google_credentials_file)
        
        # Validate access
        if not sheets_reader.validate_access(spreadsheet_id):
            return {'error': 'Failed to access Google Spreadsheet'}
        
        # Read emails
        emails = sheets_reader.read_emails(spreadsheet_id, range_name)
        
        if not emails:
            return {'error': 'No emails found in spreadsheet'}
        
        # Process emails
        return self.process_emails(emails, initialize_mode)
    
    def load_processed_emails(self) -> Set[str]:
        """Load the list of already processed emails."""
        try:
            if os.path.exists(self.processed_emails_file):
                with open(self.processed_emails_file, 'r') as f:
                    return set(json.load(f))
            return set()
        except Exception as e:
            print(f"Error loading processed emails: {e}")
            return set()
    
    def save_processed_emails(self, processed_emails: Set[str]) -> None:
        """Save the list of processed emails."""
        try:
            with open(self.processed_emails_file, 'w') as f:
                json.dump(list(processed_emails), f, indent=2)
        except Exception as e:
            print(f"Error saving processed emails: {e}")
    
    def log_successful_unsubscribe(self, email: str) -> None:
        """Log a successful unsubscribe to the log file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] Successfully unsubscribed: {email}\n"
            
            with open(self.success_log_file, 'a') as f:
                f.write(log_entry)
            
            print(f"Logged successful unsubscribe: {email}")
        except Exception as e:
            print(f"Error logging successful unsubscribe: {e}")
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            print("Error: Refresh token not available.")
            return False
        
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.config.constant_contact_api_key,
                'client_secret': self.config.constant_contact_client_secret
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            print("Attempting to refresh access token...")
            response = requests.post(self.AUTH_URL, data=data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.refresh_token = token_data['refresh_token']
                
                print("Successfully refreshed access token!")
                return True
            else:
                print(f"Failed to refresh access token. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error refreshing access token: {e}")
            return False
    
    def get_contact_id(self, email: str) -> Optional[str]:
        """Get the contact ID for a given email address."""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        params = {'email': email}
        
        try:
            print(f"Searching for contact with email: {email}")
            response = requests.get(f"{self.BASE_URL}/contacts", headers=headers, params=params)
            
            # Handle token expiry
            if response.status_code == 401:
                print("Access token expired. Attempting to refresh...")
                if self.refresh_access_token():
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.get(f"{self.BASE_URL}/contacts", headers=headers, params=params)
                else:
                    return None
            
            # Handle bad request
            if response.status_code == 400:
                print(f"Bad Request Error when searching for {email}")
                return None
            
            response.raise_for_status()
            
            data = response.json()
            contacts = data.get('contacts', [])
            
            if not contacts:
                print(f"No contact found with email: {email}")
                return None
            
            contact_id = contacts[0].get('contact_id')
            if contact_id:
                print(f"Found contact ID: {contact_id}")
            return contact_id
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching for contact {email}: {e}")
            return None
    
    def unsubscribe_contact(self, contact_id: str) -> bool:
        """Unsubscribe a contact using their contact ID."""
        if not contact_id:
            return False
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            print(f"Unsubscribing contact with ID: {contact_id}")
            
            # Get contact details first
            get_response = requests.get(f"{self.BASE_URL}/contacts/{contact_id}", headers=headers)
            
            # Handle token expiry
            if get_response.status_code == 401:
                if self.refresh_access_token():
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    get_response = requests.get(f"{self.BASE_URL}/contacts/{contact_id}", headers=headers)
                else:
                    return False
            
            if get_response.status_code == 404:
                print(f"Contact ID {contact_id} not found.")
                return False
            
            get_response.raise_for_status()
            
            # Try multiple approaches to unsubscribe
            contact_data = get_response.json()
            email_address = contact_data.get('email_address', {}).get('address', 'Unknown email')
            print(f"Retrieved contact details for: {email_address}")
            
            # Approach 1: Update with permission_to_send
            updated_contact = contact_data.copy()
            if 'email_address' in updated_contact:
                updated_contact['email_address']['permission_to_send'] = 'implicit'
                updated_contact['email_address']['opt_out_source'] = 'Contact'
                updated_contact['email_address']['opt_out_date'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            
            updated_contact['update_source'] = 'Contact'
            updated_contact['list_memberships'] = []
            
            response = requests.put(f"{self.BASE_URL}/contacts/{contact_id}", headers=headers, json=updated_contact)
            
            # Handle token expiry
            if response.status_code == 401:
                if self.refresh_access_token():
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.put(f"{self.BASE_URL}/contacts/{contact_id}", headers=headers, json=updated_contact)
                else:
                    return False
            
            if response.status_code < 400:
                print("Successfully updated contact with unsubscribe status")
                return True
            
            # Approach 2: Try different permission value
            print("Trying alternative permission value...")
            if 'email_address' in updated_contact:
                updated_contact['email_address']['permission_to_send'] = 'unsubscribed'
            
            alt_response = requests.put(f"{self.BASE_URL}/contacts/{contact_id}", headers=headers, json=updated_contact)
            
            if alt_response.status_code == 401 and self.refresh_access_token():
                headers['Authorization'] = f'Bearer {self.access_token}'
                alt_response = requests.put(f"{self.BASE_URL}/contacts/{contact_id}", headers=headers, json=updated_contact)
            
            if alt_response.status_code < 400:
                print("Successfully updated contact with unsubscribe status")
                return True
            
            # Approach 3: Status endpoint
            print("Trying direct contact status update...")
            status_data = {"status": "OPTOUT", "source": "Contact"}
            status_response = requests.patch(f"{self.BASE_URL}/contacts/{contact_id}/status", headers=headers, json=status_data)
            
            if status_response.status_code == 401 and self.refresh_access_token():
                headers['Authorization'] = f'Bearer {self.access_token}'
                status_response = requests.patch(f"{self.BASE_URL}/contacts/{contact_id}/status", headers=headers, json=status_data)
            
            if status_response.status_code < 400:
                print("Successfully updated contact status to OPTOUT")
                return True
            
            print("All approaches failed. Unable to unsubscribe contact.")
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"Error unsubscribing contact {contact_id}: {e}")
            return False
    
    def process_emails(self, emails: List[str], initialize_mode: bool = False) -> Dict[str, Any]:
        """
        Process a list of emails for unsubscribing.
        
        Args:
            emails: List of email addresses to process.
            initialize_mode: If True, just mark emails as processed without unsubscribing.
            
        Returns:
            Dictionary with processing results.
        """
        # Load already processed emails
        processed_emails = self.load_processed_emails()
        print(f"Found {len(processed_emails)} previously processed emails.")
        
        if initialize_mode:
            print(f"\n🔄 INITIALIZING: Marking all {len(emails)} current emails as already processed...")
            for email in emails:
                processed_emails.add(email)
            
            self.save_processed_emails(processed_emails)
            
            return {
                'initialized': len(emails),
                'message': f"Marked {len(emails)} emails as already processed"
            }
        
        # Filter out already processed emails
        new_emails = [email for email in emails if email not in processed_emails]
        
        if not new_emails:
            return {
                'new_emails': 0,
                'message': "No new emails to process"
            }
        
        print(f"Found {len(new_emails)} new emails to process.")
        
        # Process each new email
        success_count = 0
        not_found_count = 0
        error_count = 0
        not_found_emails = []
        
        rate_limit = self.config.rate_limit_seconds
        
        for i, email in enumerate(new_emails, 1):
            print(f"Processing {i}/{len(new_emails)}: {email}")
            
            # Get contact ID
            contact_id = self.get_contact_id(email)
            
            if not contact_id:
                print(f"  Contact not found for {email}")
                not_found_count += 1
                not_found_emails.append(email)
                processed_emails.add(email)
                
                if i < len(new_emails):
                    time.sleep(rate_limit)
                continue
            
            # Unsubscribe contact
            if self.unsubscribe_contact(contact_id):
                print(f"  Successfully unsubscribed {email}")
                success_count += 1
                self.log_successful_unsubscribe(email)
            else:
                print(f"  Failed to unsubscribe {email}")
                error_count += 1
            
            # Mark email as processed
            processed_emails.add(email)
            
            # Rate limiting
            if i < len(new_emails):
                time.sleep(rate_limit)
        
        # Save the updated processed emails list
        self.save_processed_emails(processed_emails)
        
        result = {
            'new_emails_processed': len(new_emails),
            'success_count': success_count,
            'not_found_count': not_found_count,
            'error_count': error_count,
            'total_processed': len(processed_emails),
            'not_found_emails': not_found_emails
        }
        
        # Print summary
        print("\nUnsubscribe Summary:")
        print(f"  New emails processed: {result['new_emails_processed']}")
        print(f"  Successfully unsubscribed: {result['success_count']}")
        print(f"  Contacts not found: {result['not_found_count']}")
        print(f"  Errors during unsubscribe: {result['error_count']}")
        print(f"  Total processed emails (all time): {result['total_processed']}")
        
        return result 