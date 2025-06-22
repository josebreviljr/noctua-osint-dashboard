import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for Noctua OSINT Collector"""
    
    # Google Gemini API Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    # Application Settings
    MAX_ARTICLES_PER_FEED = int(os.getenv('MAX_ARTICLES_PER_FEED', '5'))
    FEEDS_FILE = os.getenv('FEEDS_FILE', 'feeds.txt')
    OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'data/reports.json')
    
    # Request Settings
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    
    @property
    def google_api_key(self):
        """Property to access Google API key"""
        return self.GOOGLE_API_KEY
    
    @classmethod
    def validate(cls, require_api_key=True):
        """Validate that required configuration is present"""
        if require_api_key and not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        return True 