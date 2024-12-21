#!/bin/bash

# Define the log format
log_header="========================="
log_footer="========================="

# Get the current time
current_time=$(date +"%Y-%m-%d %H:%M:%S")

# Get the Python version
python_version=$(python --version 2>&1)

# Get the Flask environment (if set, otherwise defaults to 'development')
flask_env=${FLASK_ENV:-Production}

# Get the current working directory
working_dir=$(pwd)

# Get the hostname of the machine
hostname=$(hostname)

# Output the formatted log
echo "$log_header"
echo "Starting Flask Server..."
echo "Current Time: $current_time"
echo "Python Version: $python_version"
echo "Server Environment: $flask_env"
echo "Working Directory: $working_dir"
echo "Hostname: $hostname"
echo "$log_footer"

# Export the ENV variable
export ENV=$flask_env

# Start the Flask server
python -m app.main
