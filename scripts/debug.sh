#!/bin/bash
# Load the .env file
export $(cat .env | xargs)

# Launch the Flask app with the desired environment
flask run --no-debugger --no-reload --port $PORT
