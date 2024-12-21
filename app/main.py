from app import create_app
from app.utils.api_consts import APIConfig


api_config = APIConfig()
app = create_app()

if __name__ == "__main__":
    app.run(port=api_config.port)
