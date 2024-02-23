import logging
import os


def setup_logger(log_file, level=logging.INFO):
    """Set up a logger with the specified log level and log file."""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Create file handler and set level to debug
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Add file handler to logger
    logger.addHandler(file_handler)

    return logger


logger = setup_logger("log.txt")
