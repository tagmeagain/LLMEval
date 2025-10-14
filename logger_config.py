"""
Logging Configuration for DeepEval
Creates timestamped log files and handles all output
"""

import logging
import sys
from datetime import datetime
import os


def setup_logger(name="deepeval", log_to_file=True, log_to_console=True, log_level=logging.INFO):
    """
    Set up logger with file and/or console output
    
    Args:
        name: Logger name
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with timestamp
    if log_to_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"deepeval_{timestamp}.log")
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Print log file location (this will go to console even if log_to_console=False)
        print(f"📝 Logging to: {log_file}")
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def log_section(logger, title, char='=', width=80):
    """Log a section separator"""
    logger.info(char * width)
    logger.info(title)
    logger.info(char * width)


def log_subsection(logger, title, char='-', width=80):
    """Log a subsection separator"""
    logger.info(title)
    logger.info(char * width)


class LoggerWriter:
    """
    Custom writer to redirect print statements to logger
    Usage: sys.stdout = LoggerWriter(logger)
    """
    def __init__(self, logger, level=logging.INFO):
        self.logger = logger
        self.level = level
        self.buffer = ''
    
    def write(self, message):
        if message and message.strip():
            # Remove ANSI color codes if present
            import re
            message = re.sub(r'\x1b\[[0-9;]*m', '', message)
            self.logger.log(self.level, message.strip())
    
    def flush(self):
        pass


def get_latest_log_file():
    """Get the path to the most recent log file"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        return None
    
    log_files = [f for f in os.listdir(log_dir) if f.startswith('deepeval_') and f.endswith('.log')]
    if not log_files:
        return None
    
    latest = sorted(log_files)[-1]
    return os.path.join(log_dir, latest)

