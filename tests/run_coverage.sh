#!/usr/bin/env bash
#
# Copyright 2023-2025 Daniel Balparda (balparda@gmail.com)
#
# https://coverage.readthedocs.io/
#

python3 -m coverage run --omit=*_test.py,*_tests.py,*/dist-packages/*,*/site-packages/* run_all_tests.py
python3 -m coverage report -m
python3 -m coverage html
