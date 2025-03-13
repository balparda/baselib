#!/bin/bash
#
# Copyright 2023 Daniel Balparda (balparda@gmail.com)
#
# https://coverage.readthedocs.io/
#

coverage run --omit=*_test.py,*_tests.py,*/dist-packages/*,*/site-packages/* run_all_tests.py
coverage report -m
coverage html
