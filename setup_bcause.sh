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

# Check if the virtual environment already exists
if [ -d "venv_bcause" ]; then
    echo "Bcause virtual environment already exists."
else
    echo "Creating a Bcause virtual environment with Python 3.10..."
    python3.10 -m venv venv_bcause
fi


echo "Activating the Bcause virtual environment..."
source venv_bcause/bin/activate


if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Bcause virtual environment activated."
else
    echo "Error: Failed to activate the Bcause virtual environment."
    exit 1
fi


echo "Installing bcause..."
if ! pip install --no-cache-dir --use-feature=fast-deps bcause; then
    echo "Error: Failed to install bcause."
    exit 1
fi

echo "All Bcause packages installed successfully in the Bcause virtual environment."

deactivate
