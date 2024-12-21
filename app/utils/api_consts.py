import os
import sys
from flask import jsonify
from dotenv import load_dotenv
from app.services.logger_service import LoggerService


logger = LoggerService()


class APIError(Exception):
    def __init__(self, response_message, logger_message, status_code=400):
        self.response_message = response_message
        self.status_code = status_code
        logger.error(logger_message)

    def __str__(self):
        return f"{self.status_code} - {self.response_message}"

    def generate_response(self):
        return jsonify({"message": self.response_message}), self.status_code


class APIWarn(Exception):
    def __init__(self, response_message, logger_message, status_code=400):
        self.response_message = response_message
        self.status_code = status_code
        logger.warning(logger_message)

    def __str__(self):
        return f"{self.status_code} - {self.response_message}"

    def generate_response(self):
        return jsonify({"message": self.response_message}), self.status_code


class APIConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIConfig, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        env = os.getenv("ENV")
        if env == "Production":
            load_dotenv(".env.prod")
        else:
            load_dotenv(".env.dev")
        self.port = self._get_validated_port()
        self.env = self._get_validated_env()

    def _get_validated_port(self):
        port_str = os.getenv("FLASK_PORT")
        try:
            port = int(port_str)
            if 1 <= port <= 65535:
                return port

            logger.error(
                "Invalid PORT value: must be between 1 and 65535",
                "INTERNAL/APIConfig",
                "_get_validated_port",
            )
        except ValueError:
            logger.error(
                "PORT value must be an integer",
                "INTERNAL/APIConfig",
                "_get_validated_port",
            )
            sys.exit(1)

    def _get_validated_env(self):
        env_str = os.getenv("FLASK_ENV")
        if env_str in ["Development", "Production"]:
            return env_str
        logger.error(
            "Invalid ENV value: must be either 'Development' or 'Production'",
            "INTERNAL/APIConfig",
            "_get_validated_env",
        )
        sys.exit(1)
