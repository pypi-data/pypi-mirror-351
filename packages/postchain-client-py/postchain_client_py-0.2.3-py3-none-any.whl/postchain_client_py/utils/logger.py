import logging
import sys
from typing import Optional

def setup_logger(verbose: bool = False) -> logging.Logger:
    """Configure and return the package logger"""
    # Configure the root logger for consistent formatting across all modules
    root_logger = logging.getLogger()
    root_logger.handlers = []
    
    if not verbose:
        # Set level higher than CRITICAL to suppress all logs
        root_logger.setLevel(logging.CRITICAL + 1)
        return root_logger
    
    # If verbose, set up normal logging
    root_logger.setLevel(logging.DEBUG)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    
    # ANSI color codes
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': BLUE,
            'INFO': GREEN,
            'WARNING': YELLOW,
            'ERROR': RED,
            'CRITICAL': RED
        }
        
        def format(self, record):
            # If the message contains byte strings, try to decode them
            if isinstance(record.msg, (bytes, bytearray)):
                try:
                    record.msg = record.msg.decode('utf-8')
                except:
                    pass
            elif isinstance(record.msg, str) and "b'" in record.msg:
                # Try to clean up byte string representations in text
                record.msg = record.msg.replace("b'", "'").replace("b\"", "\"")
            
            # Add color to the level name
            color = self.COLORS.get(record.levelname, '')
            if color:
                record.levelname = f"{color}{record.levelname}{RESET}"
            
            return super().format(record)
    
    handler.setFormatter(ColoredFormatter(
        '%(asctime)s [%(levelname)8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Add handler to root logger
    root_logger.addHandler(handler)
    
    # Also configure the package logger to inherit from root
    logger = logging.getLogger('postchain_client_py')
    logger.handlers = []  # Remove any existing handlers
    logger.propagate = True  # Ensure it uses root logger's handlers
    
    # Set asyncio logger to a higher level to suppress implementation details
    logging.getLogger('asyncio').setLevel(logging.INFO)
    
    return logger

# Create default logger instance
logger = setup_logger()

def set_verbose(verbose: bool = True):
    """Update logger verbosity level"""
    global logger
    logger = setup_logger(verbose) 