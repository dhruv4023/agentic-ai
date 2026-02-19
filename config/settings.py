import os
from dotenv import load_dotenv
import logging

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SPRING_API_BASE = os.getenv("SPRING_API_BASE")
    SESSION_SECRET = os.getenv("SESSION_SECRET")
    AI_SERVICE_KEY = os.getenv("AI_SERVICE_KEY")
    AI_SERVICE_SECRET = os.getenv("AI_SERVICE_SECRET")
    DEBUG = (
        os.environ.get("DEBUG").lower() == "true" if os.environ.get("DEBUG") else False
    )



class LOG:
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


if Settings.DEBUG:
    LOG.configure_logging(logging.DEBUG)


settings = Settings()
log = LOG()