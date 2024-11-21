#!/bin/bash

# Check if Python 3.10 is installed
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

# Check if the virtual environment already exists
if [ -d "venv_dowhy" ]; then
    echo "DoWhy virtual environment already exists."
else
    echo "Creating a DoWhy virtual environment with Python 3.10..."
    python3.10 -m venv venv_dowhy

    echo "Activating the DoWhy virtual environment..."
    source venv_dowhy/bin/activate

    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "DoWhy virtual environment activated."
    else
        echo "Error: Failed to activate the DoWhy virtual environment."
        exit 1
    fi

    echo "Installing dowhy..."
    if ! pip install --no-cache-dir --use-feature=fast-deps dowhy; then
        echo "Error: Failed to install dowhy."
        exit 1
    fi

    echo "All DoWhy packages installed successfully in the DoWhy virtual environment."
    deactivate
fi
