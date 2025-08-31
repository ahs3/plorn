#!/bin/bash

echo
echo "=== config tests ==="
python -m unittest tests/config_tests.py

echo
echo "=== db tests ==="
python -m unittest tests/db_tests.py
