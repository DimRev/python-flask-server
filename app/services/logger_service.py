import logging
import inspect
import os
from datetime import datetime
from flask import request


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to colorize log levels, routes, and functions using ASCII escape codes.
    """

    COLOR_CODES = {
        "DEBUG": "\033[1;37;44m ",  # White foreground, Blue background
        "INFO": "\033[1;30;46m ",  # Black foreground, Cyan background
        "WARNING": "\033[1;30;43m ",  # Black foreground, Yellow background
        "ERROR": "\033[1;37;41m ",  # White foreground, Red background
        "CRITICAL": "\033[1;37;45m ",  # White foreground, Magenta background
    }

    AGENT_COLOR_CODE = "\033[1;30;43m "  # Black foreground, Cyan background

    RESET_CODE = " \033[0m"

    def format(self, record):
        # Add color to the level name, route, and function
        levelname = record.levelname
        if levelname in self.COLOR_CODES:
            color = self.COLOR_CODES[levelname]
            record.levelname = f"{color}{levelname}{self.RESET_CODE}"
            record.route = f"{color}{record.route}{self.RESET_CODE}"
            record.function = f"{color}{record.function}{self.RESET_CODE}"
            record.ip = f"{self.AGENT_COLOR_CODE}{record.ip}{self.RESET_CODE}"
            record.user_agent = (
                f"{self.AGENT_COLOR_CODE}{record.user_agent}{self.RESET_CODE}"
            )

        return super().format(record)


class LoggerService:
    _instance = None  # Singleton instance

    def __new__(cls, name="AppLogger"):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(name)  # Initialize the instance
        return cls._instance

    def __init__(self, name="AppLogger"):
        if not hasattr(self, "logger"):  # Avoid reinitializing the logger
            self.logger = logging.getLogger(name)
            self.logger.setLevel(logging.DEBUG)

            # Ensure the logs directory exists
            log_dir = "./logs"
            os.makedirs(log_dir, exist_ok=True)

            # Get today's date for the log file name
            log_file = os.path.join(
                log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"
            )

            # Log format
            formatter = ColoredFormatter(
                "%(asctime)s - %(levelname)s - %(route)s %(function)s - %(log_message)s - %(ip)s - %(user_agent)s"
            )

            # File handler (write to date-based log file)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s %(route)s %(function)s - %(log_message)s - %(ip)s - %(user_agent)s"
                )
            )

            # Stream handler (colored for console output)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            # Add handlers to logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def log(self, level, message, route=None, func=None):
        if isinstance(message, list):
            message = " | ".join(map(str, message))  # Format list as a string

        # Get route and function details if not provided
        if not route:
            route = request.path if request else "Unknown"
        if not func:
            func = inspect.stack()[1].function
            curr_stack_idx = 1
            while func in [
                "log",
                "debug",
                "info",
                "warning",
                "error",
                "critical",
                "exception",
                "__init__",
            ]:
                curr_stack_idx += 1
                func = inspect.stack()[curr_stack_idx].function

        # Capture the user's IP and user agent
        ip = request.remote_addr if request else "Unknown IP"
        user_agent = request.user_agent.string if request else "Unknown Agent"

        # Use 'extra' to pass custom fields to the logger
        extra = {
            "route": route,
            "function": func,
            "log_message": message,  # Use 'log_message' instead of 'message'
            "ip": ip,
            "user_agent": user_agent,
        }
        self.logger.log(level, message, extra=extra)

    def debug(self, message, route=None, func=None):
        self.log(logging.DEBUG, message, route, func)

    def info(self, message, route=None, func=None):
        self.log(logging.INFO, message, route, func)

    def warning(self, message, route=None, func=None):
        self.log(logging.WARNING, message, route, func)

    def error(self, message, route=None, func=None):
        self.log(logging.ERROR, message, route, func)

    def critical(self, message, route=None, func=None):
        self.log(logging.CRITICAL, message, route, func)
