#!/bin/bash
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

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
