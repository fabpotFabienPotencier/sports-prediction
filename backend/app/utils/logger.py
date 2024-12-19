import logging
import sys
from typing import Optional

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )

def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or __name__) 