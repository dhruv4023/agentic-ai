import os
from dotenv import load_dotenv
import logging
from huggingface_hub import login

load_dotenv()

class VectorSearchConfig:
    DB_NAME = os.getenv("VECTOR_SEARCH_DB_NAME") or "code_notes_ai"
    COLLECTION = os.getenv("VECTOR_SEARCH_COLLECTION") or "note_vectors"
    INDEX_NAME = os.getenv("VECTOR_SEARCH_INDEX_NAME") or "default"


class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SPRING_API_BASE = os.getenv("SPRING_API_BASE")
    HUGGINGFACEHUB_API_TOKEN = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    SESSION_SECRET = os.getenv("SESSION_SECRET")
    AI_SERVICE_KEY = os.getenv("AI_SERVICE_KEY")
    AI_SERVICE_SECRET = os.getenv("AI_SERVICE_SECRET")
    MONGO_URI = os.getenv("MONGO_URI")
    DEBUG = os.environ.get("DEBUG").lower() == "true" if os.environ.get("DEBUG") else False
    VECTOR_SEARCH = VectorSearchConfig()


class Log:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def configure_logging(level=logging.INFO):
        logging.basicConfig(level=level)  # Set the logging level
        
    @staticmethod
    def debug(msg):
        logging.debug(msg)
        
    @staticmethod
    def info(msg):
        logging.info(msg)
        
    @staticmethod
    def warning(msg):
        logging.warning(msg)
        
    @staticmethod
    def error(msg):
        logging.error(msg)
        
    @staticmethod
    def critical(msg):
        logging.critical(msg)


SETTING = Settings()
LOG = Log()

LOG.configure_logging(logging.DEBUG if SETTING.DEBUG else logging.INFO)

login(
    token=SETTING.HUGGINGFACEHUB_API_TOKEN,
    add_to_git_credential=True,
)
