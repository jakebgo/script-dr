import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Data source paths
    DATA_SOURCE_PATH = os.getenv('DATA_SOURCE_PATH', './data')
    OUTPUT_PATH = os.getenv('OUTPUT_PATH', './output')
    
    # Ingestion settings
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '1000'))
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
    
    # File patterns
    DATA_FILE_PATTERN = os.getenv('DATA_FILE_PATTERN', '*.csv')
    
    # API Keys
    GEMINI_FLASH_API_KEY = os.getenv('GEMINI_FLASH_API_KEY', 'AIzaSyCjSYofyaKU9fUPRcwedTcK5gnho12P97Q')
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        os.makedirs(cls.DATA_SOURCE_PATH, exist_ok=True)
        os.makedirs(cls.OUTPUT_PATH, exist_ok=True) 