# audio_processing/utils.py

import logging

def setup_logging():
    """
    Sets up the logging configuration for the application.
    This function will configure logging to output messages to the console
    and optionally to a file, with timestamps, log levels, and log messages.
    """
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(),  # Output logs to the console
            logging.FileHandler('logs/audio_processing.log', mode='a')  # Output logs to a file
        ]
    )

    # Create a logger instance to be used across the application
    logger = logging.getLogger(__name__)

    logger.info("Logging setup complete.")

# Optionally, you can define more utility functions here, such as file validation, or others.

