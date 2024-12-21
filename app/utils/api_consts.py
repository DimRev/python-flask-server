import os
import sys
from enum import Enum
from dotenv import load_dotenv
from app.services.logger_service import LoggerService

logger = LoggerService()


class Environment(Enum):
    DEVELOPMENT = "Development"
    PRODUCTION = "Production"


class APIConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self._load_env_file()
        self._port = self._get_validated_port()
        self._env = self._get_validated_env()

    def _load_env_file(self):
        env = os.getenv("ENV")
        if env == Environment.PRODUCTION.value:
            load_dotenv(".env.prod")
        else:
            load_dotenv(".env.dev")

    def _get_validated_port(self):
        port_str = os.getenv("FLASK_PORT")
        if not port_str:
            self._exit_with_error("FLASK_PORT is missing", "_get_validated_port")
        try:
            port = int(port_str)
            if 1 <= port <= 65535:
                return port
        except ValueError:
            self._exit_with_error(
                "FLASK_PORT must be an integer between 1 and 65535",
                "_get_validated_port",
            )

    def _get_validated_env(self):
        env_str = os.getenv("FLASK_ENV")
        if env_str in {e.value for e in Environment}:
            return env_str
        self._exit_with_error(
            f"FLASK_ENV must be one of {', '.join(e.value for e in Environment)}",
            "_get_validated_env",
        )

    def _exit_with_error(self, message, validator):
        logger.error(message, route="INTERNAL/APIConfig", func=validator)
        sys.exit(1)

    @property
    def port(self):
        return self._port

    @property
    def env(self):
        return self._env
