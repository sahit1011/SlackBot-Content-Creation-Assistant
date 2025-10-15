# app/config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Slack
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
    SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')

    # Database
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    # Redis
    REDIS_URL = os.getenv('REDIS_URL')

    # APIs
    BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL')

    # Application Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_KEYWORDS = int(os.getenv('MAX_KEYWORDS', '1000'))
    MAX_CLUSTERS = int(os.getenv('MAX_CLUSTERS', '10'))
    PROCESSING_TIMEOUT = int(os.getenv('PROCESSING_TIMEOUT', '600'))  # 10 minutes

    # Health Check
    HEALTH_CHECK_PORT = int(os.getenv('HEALTH_CHECK_PORT', '3000'))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = [
            'SLACK_BOT_TOKEN',
            'SLACK_SIGNING_SECRET',
            'SUPABASE_URL',
            'SUPABASE_KEY'
        ]

        missing = [var for var in required if not getattr(cls, var)]

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        return True