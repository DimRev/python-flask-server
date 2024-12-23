#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to handle errors
handle_error() {
    echo "An error occurred in the script at line $1."
    echo "Please check the logs above for details."
    exit 1
}

# Trap errors and call the error handler
trap 'handle_error $LINENO' ERR

echo "Creating drivers directory..."
mkdir -p ./drivers/chromedriver
echo "Directory created."

echo "Downloading ChromeDriver..."
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/131.0.6778.204/linux64/chromedriver-linux64.zip -O ./drivers/chromedriver-linux64.zip 
echo "Download complete."

echo "Extracting ChromeDriver..."
unzip ./drivers/chromedriver-linux64.zip -d ./drivers/chromedriver
echo "Extraction complete."

echo "Setting executable permissions..."
chmod +x drivers/chromedriver/chromedriver-linux64/chromedriver
echo "Permissions set."

echo "Cleaning up..."
rm -rf ./drivers/chromedriver-linux64.zip
echo "Cleanup complete."

echo "ChromeDriver setup completed successfully!"
