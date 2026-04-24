#!/bin/bash
# Install testing and formatting dependencies
pip install autopep8 flake8 pytest

# Format Python files
autopep8 --in-place --aggressive --aggressive --recursive .

# Check linting
flake8 .

# Run unit tests
pytest
