#!/bin/env sh
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################
#
#  this script was originally created for development use; not sure
#  it's the best idea for day-to-day use, however
#

SITEPKGS=$(python3 -c \
   'import sysconfig; print(sysconfig.get_paths()["purelib"])' 1>/dev/null)

if [ ! -d ${SITEPKGS}/plorn ]
then
	export PYTHONPATH=./src:${PYTHONPATH}
fi


echo
echo "=== module tests ==="
python -m unittest tests/base_obj_tests.py

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
