from app import create_app
from app.utils.api_consts import APIConfig

app = create_app()
api_config = APIConfig()

if __name__ == "__main__":
    app.run(port=api_config.port)
