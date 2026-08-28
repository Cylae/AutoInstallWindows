#!/bin/bash
pip install autopep8 flake8 pytest autoflake
autopep8 --in-place --aggressive --aggressive build.py personalize.py test_build.py test_personalize.py
autoflake --in-place --remove-all-unused-imports build.py personalize.py test_build.py test_personalize.py
flake8 build.py personalize.py test_build.py test_personalize.py
pytest
