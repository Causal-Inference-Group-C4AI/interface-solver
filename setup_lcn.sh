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


echo "Creating a LCN virtual environment with Python 3.10..."
python3.10 -m venv venv_lcn


echo "Activating the LCN virtual environment..."
source venv_lcn/bin/activate


if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "LCN virtual environment activated."
else
    echo "Error: Failed to activate the LCN virtual environment."
    exit 1
fi


echo "Installing LCN dependencies from requirements_lcn.txt..."
if ! pip install --no-cache-dir --use-feature=fast-deps -r requirements_lcn.txt; then
    echo "Error: Failed to install LCN dependencies from requirements_lcn.txt."
    exit 1
fi

echo "All LCN packages installed successfully in the LCN virtual environment."

deactivate
