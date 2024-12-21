import logging
import os
from datetime import datetime


class CrawlerLogger:
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name="CrawlerLogger", identifier=None, sub_identifier="Default"):
        if not hasattr(self, "logger"):  # Avoid reinitializing the logger
            self.logger = logging.getLogger(name)
            self.logger.setLevel(logging.DEBUG)

            # If identifier is None, set a default identifier
            self.identifier = (
                identifier if identifier is not None else "default_identifier"
            )
            self.sub_identifier = sub_identifier

            # Ensure the logs directory exists
            log_dir = f"./crawl/{self.identifier}/{self.sub_identifier}"
            os.makedirs(log_dir, exist_ok=True)

            # Get today's date for the log file name
            log_file = os.path.join(
                log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"
            )

            # Log format for both file and console handlers (no colors)
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(identifier)s %(sub_identifier)s - %(log_message)s"
            )

            # File handler (write to date-based log file)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)

            # Stream handler (no colors for console output)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            # Add handlers to logger
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def set_sub_identifier(self, sub_identifier):
        # Ensure that sub_identifier is not None
        if sub_identifier is None:
            raise ValueError("sub_identifier cannot be None")

        # Update the sub_identifier for the logger
        self.sub_identifier = sub_identifier

        log_dir = f"./crawl/{self.identifier}/{self.sub_identifier}"
        os.makedirs(log_dir, exist_ok=True)  # Ensure the log directory exists

        # Get today's date for the log file name
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

        # Remove old file handler if present (optional, based on your use case)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                self.logger.removeHandler(handler)

        # File handler (write to date-based log file)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(identifier)s %(sub_identifier)s - %(log_message)s"
            )
        )
        self.logger.addHandler(file_handler)

    def log(self, level, message, sub_identifier=None):
        if sub_identifier is not None:
            self.set_sub_identifier(sub_identifier)

        if isinstance(message, list):
            message = " | ".join(map(str, message))  # Format list as a string

        # Use 'extra' to pass custom fields to the logger
        extra = {
            "log_message": message,  # Use 'log_message' instead of 'message'
            "identifier": self.identifier,  # Add identifier to extra fields
            "sub_identifier": self.sub_identifier,  # Add sub_identifier to extra fields
        }
        self.logger.log(level, message, extra=extra)

    def debug(self, message, sub_identifier=None):
        self.log(logging.DEBUG, message, sub_identifier)

    def info(self, message, sub_identifier=None):
        self.log(logging.INFO, message, sub_identifier)

    def warning(self, message, sub_identifier=None):
        self.log(logging.WARNING, message, sub_identifier)

    def error(self, message, sub_identifier=None):
        self.log(logging.ERROR, message, sub_identifier)

    def critical(self, message, sub_identifier=None):
        self.log(logging.CRITICAL, message, sub_identifier)
