import logging

from resources.constants import FILE_PATHS
from datetime import datetime

def setup_logger(name: str, log_file: str, file_level=logging.INFO, console_level=logging.INFO) -> logging.Logger:
    """
    Set up a logger that outputs to both file and console with different levels.

    INPUTS:
        name (str): Name of the logger.
        log_file (str): Path to the log file.
        file_level (int): Logging level for the file handler (default: logging.INFO). See Log level options below.
        console_level (int): Logging level for the console handler (default: logging.INFO). See Log level options below.
    OUTPUT:
        logging.Logger: Configured logger instance.

    When a log level is selected, all logs at this level and above will be sent to the corresponding handler.
    LOG LEVELS OPTIONS:
        logging.CRITICAL: A very serious error, indicating that the program itself may be unable to continue running.
        logging.ERROR: Due to a more serious problem, the software has not been able to perform some function.
        logging.WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk full’ warnings).
        logging.INFO: Confirmation that things are working as expected.
        logging.DEBUG: Detailed information, typically of interest only when diagnosing problems.   
    """
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set to lowest level to capture everything
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Avoid adding handlers multiple times
    if not logger.handlers:
        # File handler - captures all logs at specified level
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler - only shows INFO and above (excludes DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# Create the logger instance once
# File gets DEBUG and above, Console gets INFO and above (no debug to console)
log_filename = f"app_{datetime.now().strftime('%Y-%m-%d')}.log"
logger = setup_logger('website_reports', FILE_PATHS['LOG_DIR'] + log_filename, file_level=logging.DEBUG, console_level=logging.INFO)