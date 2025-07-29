import logging
from typing import Optional

def setup_logger(name: str, log_level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File handler if specified
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger
