"""
logger.py

This module contains the logging utility functions used to set up the logger and log events.
"""
import logging


def setup_logger(filename: str, debug: bool = False) -> None:
    """Set up the configuration settings for the logger and return it."""
    logger_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=logger_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(filename),
            logging.StreamHandler()
        ]
    )
