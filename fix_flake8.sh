#!/bin/bash
# We'll just run autopep8 to quickly fix formatting issues.
pip install autopep8
autopep8 --in-place --aggressive --aggressive build.py personalize.py
