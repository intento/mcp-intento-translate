import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Intento API configuration
INTENTO_API_KEY = os.getenv('INTENTO_API_KEY')
INTENTO_API_URL = 'https://syncwrapper.inten.to/ai/text/translate' # 'https://api.inten.to/ai/text/translate'

# Validate configuration
if not INTENTO_API_KEY:
    raise ValueError("INTENTO_API_KEY environment variable is not set") 