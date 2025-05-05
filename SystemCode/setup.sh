#!/bin/bash

# Check if Python 3.12 is available
if ! command -v python3.12 &> /dev/null; then
    echo "Python 3.12 is required but not found. Please install Python 3.12 first."
    exit 1
fi

# Create virtual environment with Python 3.12
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install PyTorch first (separately to ensure proper installation)
pip install torch==2.2.1

# Install other requirements
pip install -r requirements.txt

# Generate dummy data
python generate_dummy_data.py

# Run the application
python run_app.py 