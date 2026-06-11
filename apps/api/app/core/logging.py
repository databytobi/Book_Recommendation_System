import logging
import sys
from app.core.config import settings

def setup_logging():
    """Configure logging for the application."""
    
    # Get log level with fallback
    log_level = getattr(settings, 'LOG_LEVEL', 'INFO')
    
    # Convert string to logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format=(
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)