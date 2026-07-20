#!/bin/env sh
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################
#
#  this script was originally created for development use; not sure
#  it's the best idea for day-to-day use, however
#

#############################################################
# NB:
#
# If you rely on test discovery -- i.e., run these tests with
# the command 'pytest tests' -- they will fail horribly and
# leave a mess of config files laying around that need to be
# cleaned up.
#
# If you run each module individually, they work fine.
#
# I do not understand why yet.  I think it may have to do
# with the fixtures being set up and conflicting when viewed
# as a single collection of tests.
#

pytest tests/test_main.py
pytest tests/test_objects.py
pytest tests/test_config.py
pytest tests/test_db.py
pytest tests/test_gui.py

