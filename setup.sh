#!/bin/bash


if ! python3.10 --version &>/dev/null; then
    echo "Python 3.10 not found. Installing Python 3.10..."

    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv python3.10-distutils


    if ! python3.10 --version &>/dev/null; then
        echo "Error: Python 3.10 installation failed."
        exit 1
    fi
else
    echo "Python 3.10 is already installed."
fi


echo "Creating a virtual environment with Python 3.10..."
python3.10 -m venv venv


echo "Activating the virtual environment..."
source venv/bin/activate


if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment activated."
else
    echo "Error: Failed to activate the virtual environment."
    exit 1
fi


echo "Installing dependencies from requirements.txt..."
if ! pip install -r requirements.txt; then
    echo "Error: Failed to install dependencies from requirements.txt."
    exit 1
fi


echo "Installing bcause..."
if ! pip install bcause; then
    echo "Error: Failed to install bcause."
    exit 1
fi

echo "All packages installed successfully in the virtual environment."
source venv/bin/activate

