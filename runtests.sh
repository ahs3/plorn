#!/bin/bash

echo
echo "=== config tests ==="
python -m unittest tests/config_tests.py

echo
echo "=== db tests ==="
python -m unittest tests/basic_db_tests.py
python -m unittest tests/album_db_tests.py
python -m unittest tests/photo_db_tests.py

echo
echo "=== attr tests ==="
python -m unittest tests/name_db_tests.py
python -m unittest tests/place_db_tests.py
python -m unittest tests/tag_db_tests.py
