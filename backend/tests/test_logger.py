import logging
import os
import tempfile
from backend.logger import setup_logger


def test_setup_logger():
    # Create a temporary log file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        log_file = temp_file.name

    try:
        # Set up logger
        logger = setup_logger(log_file)

        # Test if logger is set up correctly
        assert logger.level == logging.INFO

        handlers = logger.handlers

        assert isinstance(handlers[0], logging.FileHandler)
        assert handlers[0].level == logging.INFO
        assert (
            handlers[0].formatter._fmt
            == "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
        )  # Checking the formatter's format string

        # Test logging
        logger.info("Test message")
        logger.warning("Warning message")

        # Check if messages are logged to the file
        with open(log_file, "r") as f:
            lines = f.readlines()
            print("LOG: ")
            print(lines)
            assert len(lines) == 2
            assert "INFO" in lines[0]
            assert "Test message" in lines[0]
            assert "WARNING" in lines[1]
            assert "Warning message" in lines[1]
    finally:
        # Clean up
        os.remove(log_file)
