from app import create_app
from app.utils.api_consts import APIConfig

from app.services.logger_service import LoggerService

logger = LoggerService()

app = create_app()
api_config = APIConfig()

if __name__ == "__main__":
    app.run(port=api_config.port)
