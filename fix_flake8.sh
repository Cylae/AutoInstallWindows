#!/bin/bash
# Install required tools
pip install autopep8 flake8 pytest

# Format code
autopep8 --in-place --recursive --aggressive --aggressive .

# Run linter
flake8 .

# Run tests
pytest
