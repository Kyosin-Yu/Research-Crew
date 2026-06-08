import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    """
    Creates a logger that writes to both terminal and a log file.
    Every module in the project will call this to get its own logger.

    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Researcher agent starting...")
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    #Terminal Handler
    # Shows INFO and above in the terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    #File Handler
    # Saves ALL logs (including DEBUG) to a timestamped file
    log_filename = f"logs/crew_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s | %(name)s | %(funcName)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger