from flask import Flask, request
from werkzeug.exceptions import NotFound
from app.routes.api_routes import api_bp
from app.utils.api_consts import APIError


def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.errorhandler(404)
    def catch_404s(error):  # Accept the exception as an argument
        # Check if the current request matches the /api prefix
        if request.path.startswith("/api"):
            # Log and return a custom 404 response
            custom_error = APIError(
                response_message="Resource not found",
                logger_message=f"404 Not Found: {request.path}",
                status_code=404,
            )
            return custom_error.generate_response()

        # If the request is not under /api, return the default 404 response
        return error

    @app.errorhandler(APIError)
    def handle_api_error(error):
        return error.generate_response()

    return app
