# RAG Chatbot API Package
import logging
import os

# Configure logging once for the entire app
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log') if os.getenv('LOG_TO_FILE', 'false').lower() == 'true' else logging.NullHandler()
    ]
)

# Create logger for the app
logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = "RAG Agent Team"
