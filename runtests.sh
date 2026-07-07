#!/bin/env sh
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################
#
#  this script was originally created for development use; not sure
#  it's the best idea for day-to-day use, however
#

pytest tests

#echo "=== module tests ==="
#python -m unittest tests/base_obj_tests.py

#echo "=== db tests ==="
#python -m unittest tests/basic_db_tests.py
#python -m unittest tests/album_db_tests.py
#python -m unittest tests/photo_db_tests.py

#echo "=== attr tests ==="
#python -m unittest tests/name_db_tests.py
#python -m unittest tests/place_db_tests.py
#python -m unittest tests/tag_db_tests.py

#echo "=== test summary ==="
#python tests/totals.py
