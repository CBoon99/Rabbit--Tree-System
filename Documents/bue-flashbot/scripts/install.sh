#!/bin/bash
set -e

# Remove any old venvs
rm -rf .venv

# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "✅ Environment ready. Activate with: source .venv/bin/activate" 