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


echo "Creating a Autobounds virtual environment with Python 3.10..."
python3.10 -m venv venv_autobounds


echo "Activating the Autobounds virtual environment..."
source venv_autobounds/bin/activate


if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Autobounds virtual environment activated."
else
    echo "Error: Failed to activate the Autobounds virtual environment."
    exit 1
fi


echo "Installing Autobounds dependencies from requirements_autobounds.txt..."
if ! pip install --no-cache-dir --use-feature=fast-deps -r requirements_autobounds.txt; then
    echo "Error: Failed to install Autobounds dependencies from requirements_autobounds.txt."
    exit 1
fi

echo "All Autobounds packages installed successfully in the Autobounds virtual environment."

deactivate
