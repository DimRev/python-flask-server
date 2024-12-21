from flask import jsonify
from app.services.logger_service import LoggerService

logger = LoggerService()


class APIException(Exception):
    def __init__(
        self,
        response_message: str,
        logger_message: str,
        status_code: int = 400,
        log_level: str = "error",
    ):
        self.response_message = response_message
        self.status_code = status_code
        self.log_level = log_level

        log_method = getattr(logger, log_level, logger.error)
        log_method(logger_message)

    def __str__(self):
        return f"{self.status_code} - {self.response_message}"

    def generate_response(self):
        response_body = {
            "message": self.response_message,
            "status": self.status_code,
        }
        return jsonify(response_body), self.status_code


class APIError(APIException):
    def __init__(
        self, response_message: str, logger_message: str, status_code: int = 400
    ):
        super().__init__(
            response_message, logger_message, status_code, log_level="error"
        )


class APIWarn(APIException):
    def __init__(
        self, response_message: str, logger_message: str, status_code: int = 400
    ):
        super().__init__(
            response_message, logger_message, status_code, log_level="warning"
        )
