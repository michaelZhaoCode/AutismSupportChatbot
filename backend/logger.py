"""
logger.py

This module contains the logging utility functions used to set up the logger and log events.
"""
import logging


def setup_logger(filename: str) -> None:
    """Set up the configuration settings for the logger and return it."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(filename),
            logging.StreamHandler()
        ]
    )
