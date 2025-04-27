#!/usr/bin/env bash
set -o errexit  # exit on first error

echo "Installing numpy first..."
pip install numpy

echo "Installing project requirements..."
pip install -r requirements.txt
