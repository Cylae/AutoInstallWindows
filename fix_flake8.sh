#!/bin/bash
# We'll just run autopep8 to quickly fix formatting issues.
pip install autopep8 flake8 pytest
autopep8 --in-place --aggressive --aggressive -r .
flake8 .
pytest
