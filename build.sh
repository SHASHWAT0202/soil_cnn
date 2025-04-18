#!/bin/bash

echo "Starting build process..."

# Determine Python version
python_version=$(python --version)
echo "Python version: $python_version"

# Install setuptools with pip directly
echo "Installing setuptools..."
pip install --upgrade pip
pip install setuptools==59.5.0

# If Python 3.12 is being used, we need to manually install distutils
if [[ $python_version == *"3.12"* ]]; then
  echo "Python 3.12 detected, installing distutils workaround..."
  pip install --upgrade setuptools wheel
  pip install packaging
fi

# Now install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo "Build process completed." 