import logging
import mxdnkey.config as config

def get_logger(name):
    """
    Creates and returns a logger with the given name.
    Log level and format are based on the settings in config.py.
    """
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, return it to avoid duplicate logs.
    if logger.handlers:
        return logger

    # Set the log level from configuration (default to DEBUG if missing)
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.DEBUG)
    logger.setLevel(log_level)

    # Create stream handler (console) with the same log level
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # Create formatter and attach it to the handler
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    )
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)

    return logger
