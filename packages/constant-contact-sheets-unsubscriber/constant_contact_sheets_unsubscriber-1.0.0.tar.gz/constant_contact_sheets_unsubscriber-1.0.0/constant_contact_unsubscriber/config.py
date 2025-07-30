"""Configuration management for Constant Contact Unsubscriber."""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration class for managing environment variables and settings."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file. If None, loads from current directory.
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
    
    @property
    def constant_contact_api_key(self) -> str:
        """Get Constant Contact API key."""
        key = os.getenv('CONSTANT_CONTACT_API_KEY')
        if not key:
            raise ValueError("CONSTANT_CONTACT_API_KEY not found in environment variables")
        return key
    
    @property
    def constant_contact_access_token(self) -> str:
        """Get Constant Contact access token."""
        token = os.getenv('CONSTANT_CONTACT_ACCESS_TOKEN')
        if not token:
            raise ValueError("CONSTANT_CONTACT_ACCESS_TOKEN not found in environment variables")
        return token
    
    @property
    def constant_contact_refresh_token(self) -> str:
        """Get Constant Contact refresh token."""
        token = os.getenv('CONSTANT_CONTACT_REFRESH_TOKEN')
        if not token:
            raise ValueError("CONSTANT_CONTACT_REFRESH_TOKEN not found in environment variables")
        return token
    
    @property
    def constant_contact_client_secret(self) -> str:
        """Get Constant Contact client secret."""
        secret = os.getenv('CONSTANT_CONTACT_CLIENT_SECRET')
        if not secret:
            raise ValueError("CONSTANT_CONTACT_CLIENT_SECRET not found in environment variables")
        return secret
    
    @property
    def constant_contact_redirect_uri(self) -> str:
        """Get Constant Contact redirect URI."""
        uri = os.getenv('CONSTANT_CONTACT_REDIRECT_URI')
        if not uri:
            raise ValueError("CONSTANT_CONTACT_REDIRECT_URI not found in environment variables")
        return uri
    
    @property
    def token_expiry(self) -> Optional[str]:
        """Get token expiry timestamp."""
        return os.getenv('TOKEN_EXPIRY', '0')
    
    @property
    def google_credentials_file(self) -> str:
        """Get Google credentials file path."""
        return os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    
    @property
    def rate_limit_seconds(self) -> int:
        """Get rate limit between API requests (seconds)."""
        return int(os.getenv('RATE_LIMIT_SECONDS', '5'))
    
    @property
    def check_interval_seconds(self) -> int:
        """Get check interval for continuous monitoring (seconds)."""
        return int(os.getenv('CHECK_INTERVAL_SECONDS', '300'))
    
    @property
    def processed_emails_file(self) -> str:
        """Get processed emails tracking file path."""
        return os.getenv('PROCESSED_EMAILS_FILE', 'processed_emails.json')
    
    @property
    def success_log_file(self) -> str:
        """Get success log file path."""
        return os.getenv('SUCCESS_LOG_FILE', 'unsubscribe_success_log.txt')
    
    def validate(self) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            True if all required config is present, False otherwise.
        """
        try:
            self.constant_contact_api_key
            self.constant_contact_access_token
            self.constant_contact_refresh_token
            self.constant_contact_client_secret
            self.constant_contact_redirect_uri
            return True
        except ValueError:
            return False
    
    def get_missing_config(self) -> list[str]:
        """
        Get list of missing required configuration variables.
        
        Returns:
            List of missing environment variable names.
        """
        missing = []
        required_vars = [
            'CONSTANT_CONTACT_API_KEY',
            'CONSTANT_CONTACT_ACCESS_TOKEN', 
            'CONSTANT_CONTACT_REFRESH_TOKEN',
            'CONSTANT_CONTACT_CLIENT_SECRET',
            'CONSTANT_CONTACT_REDIRECT_URI'
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        return missing 